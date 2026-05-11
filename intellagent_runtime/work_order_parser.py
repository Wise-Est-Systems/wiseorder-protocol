"""Markdown work-order parser for the WiseOrder runtime core.

Parses a structured WORK ORDER markdown document into a typed
:class:`WorkOrder` record. The parser is deliberately conservative: it
extracts fields that have stable surface syntax and refuses orders that
omit a required field or that grant themselves dangerous permissions.

Surface syntax handled:

  - Title from the first line beginning ``# WORK ORDER`` or ``# ``.
  - Sections delimited by markdown headings (``##`` / ``###``) or by
    bold labels of the form ``Objective:`` at the start of a line.
  - Fenced ``` ```bash ``` and ``` ``` ``` code blocks treated as
    required commands.
  - Numbered or bulleted lists under labeled sections treated as items.

Rejection rules (raise :class:`WorkOrderError`):

  - missing objective
  - missing stop condition
  - completely empty work order
  - protected-path also listed as mutable without a permission sentence
  - deliverables that contain only placeholder markers (``TODO``,
    ``FIXME``, the literal three-dot ellipsis as a deliverable, or the
    exact text ``placeholder``)
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------


class WorkOrderError(ValueError):
    """Raised when a work-order document is malformed or unsafe."""


@dataclass
class WorkOrder:
    """A parsed WiseOrder work order.

    Every field is either populated from the source markdown or left as
    an empty sequence/empty string. The :func:`parse_work_order` function
    is the only supported way to construct a non-empty ``WorkOrder``.
    """

    title: str = ""
    objective: str = ""
    primary_rules: list[str] = field(default_factory=list)
    allowed_actions: list[str] = field(default_factory=list)
    forbidden_actions: list[str] = field(default_factory=list)
    required_outputs: list[str] = field(default_factory=list)
    required_commands: list[str] = field(default_factory=list)
    stop_condition: str = ""
    protected_paths: list[str] = field(default_factory=list)
    mutable_paths: list[str] = field(default_factory=list)
    final_reporting: list[str] = field(default_factory=list)
    source_text: str = ""
    source_sha256: str = ""

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "objective": self.objective,
            "primary_rules": list(self.primary_rules),
            "allowed_actions": list(self.allowed_actions),
            "forbidden_actions": list(self.forbidden_actions),
            "required_outputs": list(self.required_outputs),
            "required_commands": list(self.required_commands),
            "stop_condition": self.stop_condition,
            "protected_paths": list(self.protected_paths),
            "mutable_paths": list(self.mutable_paths),
            "final_reporting": list(self.final_reporting),
            "source_sha256": self.source_sha256,
        }


# ---------------------------------------------------------------------------
# Parsing internals
# ---------------------------------------------------------------------------

_PLACEHOLDER_TOKENS = ("TODO", "FIXME", "placeholder", "PLACEHOLDER", "...")

_TITLE_RE = re.compile(r"^\s*#\s+(.+?)\s*$")
_HEADING_RE = re.compile(r"^\s*(#{2,4})\s+(.+?)\s*$")
_LABEL_RE = re.compile(r"^([A-Z][A-Za-z _/-]{2,40}):\s*(.*)$")
_FENCE_OPEN = re.compile(r"^\s*```(\w+)?\s*$")
_FENCE_CLOSE = re.compile(r"^\s*```\s*$")
_BULLET_RE = re.compile(r"^\s*[-*]\s+(.*?)\s*$")
_NUMBERED_RE = re.compile(r"^\s*\d+\.\s+(.*?)\s*$")

# Labels we treat as section anchors. The mapping is intentionally
# defensive — multiple natural-language forms map to the same internal
# section, so a writer does not need to memorize one convention.
_SECTION_ALIASES = {
    "objective": "objective",
    "goal": "objective",
    "primary rule": "primary_rules",
    "primary rules": "primary_rules",
    "rule": "primary_rules",
    "rules": "primary_rules",
    "allowed actions": "allowed_actions",
    "allowed": "allowed_actions",
    "may modify": "mutable_paths",
    "mutable paths": "mutable_paths",
    "forbidden actions": "forbidden_actions",
    "forbidden": "forbidden_actions",
    "do not modify": "protected_paths",
    "do not": "forbidden_actions",
    "do not change": "protected_paths",
    "protected paths": "protected_paths",
    "required outputs": "required_outputs",
    "required output": "required_outputs",
    "outputs": "required_outputs",
    "required commands": "required_commands",
    "required final commands": "required_commands",
    "commands": "required_commands",
    "final commands": "required_commands",
    "required reporting": "final_reporting",
    "final output": "final_reporting",
    "final reporting": "final_reporting",
    "reports": "final_reporting",
    "stop": "stop_condition",
    "stop condition": "stop_condition",
}

# Lines whose lowercase form matches one of these are themselves stop markers.
_STOP_MARKERS = ("stop.", "stop", "stop the run", "halt", "terminate")


def _is_stop_marker(line: str) -> bool:
    stripped = line.strip().lower().rstrip(".")
    return stripped in {m.rstrip(".") for m in _STOP_MARKERS}


def _normalize_label(label: str) -> str | None:
    key = label.strip().lower().rstrip(".:")
    # Exact match first.
    if key in _SECTION_ALIASES:
        return _SECTION_ALIASES[key]
    # Tolerate plural / suffix variants.
    for k, target in _SECTION_ALIASES.items():
        if key == k or key.startswith(k + " "):
            return target
    return None


def _strip_inline_code(s: str) -> str:
    return re.sub(r"`([^`]*)`", r"\1", s)


def _looks_like_path(token: str) -> bool:
    if not token:
        return False
    # Heuristic: contains `/`, ends with `**`, or is a known file name.
    if "/" in token or token.endswith("**") or token.endswith("/"):
        return True
    if re.fullmatch(r"[A-Za-z0-9_.-]+\.(md|json|py|rs|go|toml|txt|yaml|yml)", token):
        return True
    return False


def _extract_paths(items: Iterable[str]) -> list[str]:
    out: list[str] = []
    for item in items:
        text = _strip_inline_code(item).strip()
        # Drop leading bullet residue if any slipped through.
        text = re.sub(r"^[-*\d.]+\s*", "", text).strip()
        # If the line is exactly a path-like token (or a quoted one), keep it.
        unquoted = text.strip("`'\"")
        if _looks_like_path(unquoted):
            out.append(unquoted)
            continue
        # Otherwise look for path-like tokens embedded in the line.
        for tok in re.findall(r"[A-Za-z0-9_./\\*-]+", text):
            if _looks_like_path(tok):
                out.append(tok)
    # Deduplicate while preserving order.
    seen: set[str] = set()
    deduped: list[str] = []
    for p in out:
        if p not in seen:
            seen.add(p)
            deduped.append(p)
    return deduped


def _has_explicit_permission(rules: Iterable[str], paths: Iterable[str]) -> bool:
    """Return True if any rule explicitly authorizes modifying any of the
    given paths. Used to distinguish a contradiction from an intentional
    exception."""
    pool = " ".join(r.lower() for r in rules)
    if not pool.strip():
        return False
    for p in paths:
        for needle in (f"may modify {p.lower()}", f"explicit permission to modify {p.lower()}"):
            if needle in pool:
                return True
    return False


def _is_pseudocode_only(item: str) -> bool:
    """Detect deliverables whose content is exclusively placeholder
    markers. Such items are rejected — the work order would commit the
    runtime to producing nothing reviewable."""
    stripped = item.strip()
    if not stripped:
        return False
    # Only flag short items that are *entirely* a placeholder marker.
    for token in _PLACEHOLDER_TOKENS:
        if stripped == token:
            return True
        # A short item that begins with the marker and has no other
        # meaningful content (just punctuation) is also placeholder-only.
        if stripped.startswith(token + " ") and len(stripped) <= len(token) + 6:
            return True
        if stripped.startswith(token + ":") and len(stripped) <= len(token) + 6:
            return True
    return False


# ---------------------------------------------------------------------------
# Parsing pipeline
# ---------------------------------------------------------------------------


@dataclass
class _Section:
    name: str
    body: list[str] = field(default_factory=list)


def _split_sections(text: str) -> list[_Section]:
    """Walk the document line-by-line and slice it into ``_Section``s.

    A new section begins when we encounter a heading or a bold label;
    code fences are treated as opaque content that is collected into the
    currently-active section.
    """
    sections: list[_Section] = []
    current = _Section(name="_prelude")
    in_fence = False
    fence_lang = ""
    for line in text.splitlines():
        if _FENCE_OPEN.match(line) and not in_fence:
            in_fence = True
            m = _FENCE_OPEN.match(line)
            fence_lang = (m.group(1) or "").lower() if m else ""
            current.body.append(line)
            continue
        if in_fence:
            current.body.append(line)
            if _FENCE_CLOSE.match(line):
                in_fence = False
                fence_lang = ""
            continue
        h = _HEADING_RE.match(line)
        if h:
            section_label = _normalize_label(h.group(2))
            if section_label:
                sections.append(current)
                current = _Section(name=section_label)
                continue
            sections.append(current)
            current = _Section(name=f"heading::{h.group(2).strip()}")
            continue
        lab = _LABEL_RE.match(line)
        if lab and not _BULLET_RE.match(line):
            section_label = _normalize_label(lab.group(1))
            if section_label:
                sections.append(current)
                current = _Section(name=section_label)
                # An inline value after the colon counts as the first
                # body line of the new section.
                rest = lab.group(2).strip()
                if rest:
                    current.body.append(rest)
                continue
        current.body.append(line)
    sections.append(current)
    # Drop empty leading prelude.
    return [s for s in sections if s.body or s.name != "_prelude"]


def _items_from_body(body: Iterable[str]) -> list[str]:
    """Extract bulleted/numbered items and code-fence contents from a
    section body."""
    items: list[str] = []
    in_fence = False
    for line in body:
        if _FENCE_OPEN.match(line) and not in_fence:
            in_fence = True
            continue
        if in_fence:
            if _FENCE_CLOSE.match(line):
                in_fence = False
                continue
            if line.strip():
                items.append(line.strip())
            continue
        b = _BULLET_RE.match(line)
        if b:
            text = b.group(1).strip()
            if text:
                items.append(text)
            continue
        n = _NUMBERED_RE.match(line)
        if n:
            text = n.group(1).strip()
            if text:
                items.append(text)
            continue
    return items


def _prose_from_body(body: Iterable[str]) -> str:
    """Join a section body into a single trimmed prose paragraph."""
    return " ".join(line.strip() for line in body if line.strip()).strip()


def _scan_global_signals(text: str) -> tuple[str, bool]:
    """Return (title, has_stop_marker) by inspecting raw lines.

    ``has_stop_marker`` is True if any non-fenced line is a Stop marker.
    """
    title = ""
    has_stop = False
    in_fence = False
    for line in text.splitlines():
        if _FENCE_OPEN.match(line) and not in_fence:
            in_fence = True
            continue
        if in_fence:
            if _FENCE_CLOSE.match(line):
                in_fence = False
            continue
        if not title:
            t = _TITLE_RE.match(line)
            if t:
                title = t.group(1).strip()
        if _is_stop_marker(line):
            has_stop = True
    return title, has_stop


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def parse_work_order(text: str) -> WorkOrder:
    """Parse ``text`` into a :class:`WorkOrder` or raise
    :class:`WorkOrderError` with a precise reason.

    The function is pure: it does not read from or write to the
    filesystem. To parse a file, call :func:`parse_work_order_file`.
    """
    if not text or not text.strip():
        raise WorkOrderError("work order is empty")

    title, has_stop = _scan_global_signals(text)
    sections = _split_sections(text)

    wo = WorkOrder(title=title)
    seen_section_names: set[str] = set()
    for s in sections:
        seen_section_names.add(s.name)
        if s.name == "objective":
            wo.objective = _prose_from_body(s.body)
        elif s.name == "primary_rules":
            wo.primary_rules.extend(_items_from_body(s.body))
        elif s.name == "allowed_actions":
            wo.allowed_actions.extend(_items_from_body(s.body))
        elif s.name == "forbidden_actions":
            wo.forbidden_actions.extend(_items_from_body(s.body))
        elif s.name == "required_outputs":
            wo.required_outputs.extend(_items_from_body(s.body))
        elif s.name == "required_commands":
            wo.required_commands.extend(_items_from_body(s.body))
        elif s.name == "stop_condition":
            wo.stop_condition = _prose_from_body(s.body) or "Stop."
        elif s.name == "protected_paths":
            wo.protected_paths.extend(_extract_paths(_items_from_body(s.body)))
        elif s.name == "mutable_paths":
            wo.mutable_paths.extend(_extract_paths(_items_from_body(s.body)))
        elif s.name == "final_reporting":
            wo.final_reporting.extend(_items_from_body(s.body))

    # A bare "Stop." marker anywhere in the document satisfies the stop
    # requirement, even without an explicit "## Stop" heading.
    if not wo.stop_condition and has_stop:
        wo.stop_condition = "Stop."

    if not wo.objective:
        raise WorkOrderError("missing required section: objective")
    if not wo.stop_condition:
        raise WorkOrderError("missing required section: stop condition")

    # Reject placeholder-only deliverables.
    placeholder_offenders = [
        item for item in wo.required_outputs + wo.final_reporting
        if _is_pseudocode_only(item)
    ]
    if placeholder_offenders:
        raise WorkOrderError(
            "work order contains placeholder-only deliverable(s): "
            + ", ".join(repr(x) for x in placeholder_offenders)
        )

    # A protected path also listed as mutable is a contradiction unless
    # the document carries an explicit per-path permission line in its
    # primary rules.
    overlap = sorted(set(wo.protected_paths) & set(wo.mutable_paths))
    if overlap and not _has_explicit_permission(wo.primary_rules, overlap):
        raise WorkOrderError(
            "protected path(s) also declared mutable without explicit permission: "
            + ", ".join(overlap)
        )

    wo.source_text = text
    wo.source_sha256 = "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()
    return wo


def parse_work_order_file(path: str | Path) -> WorkOrder:
    """Read ``path`` and parse it. Raises :class:`WorkOrderError` on
    malformed input and :class:`FileNotFoundError` if the path is absent.
    """
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    return parse_work_order(text)


# ---------------------------------------------------------------------------
# Self-check
# ---------------------------------------------------------------------------


_SELF_CHECK_VALID = """# WORK ORDER X — Demo
## Objective
Demonstrate the parser end-to-end.

## Primary Rules
- Do not modify SPEC.md.
- Real code only.

## Allowed Actions
- Edit `intellagent_runtime/`.

## Forbidden Actions
- Delete vectors/

## Required Outputs
- A report at `reports/runtime_core/demo.md`.

## Required Commands
```bash
make ci
```

## Do Not Modify
- vectors/**
- canonicalization/corpus/**

## Final Output
Print a summary.

Stop.
"""


def self_check() -> int:
    """Run a minimal end-to-end exercise and report 0 (ok) or 1 (fail)."""
    failures: list[str] = []

    def expect(name: str, condition: bool, detail: str = "") -> None:
        print(f"  [{'PASS' if condition else 'FAIL'}] {name}")
        if not condition:
            failures.append(f"{name}: {detail}")

    wo = parse_work_order(_SELF_CHECK_VALID)
    expect("title_extracted", wo.title.startswith("WORK ORDER X"), wo.title)
    expect("objective_extracted", wo.objective != "", wo.objective)
    expect("primary_rules_count", len(wo.primary_rules) >= 2)
    expect("required_commands_seen", "make ci" in wo.required_commands)
    expect("protected_paths_seen", "vectors/**" in wo.protected_paths)
    expect("stop_condition_seen", wo.stop_condition == "Stop.")
    expect("source_sha256_set", wo.source_sha256.startswith("sha256:"))

    # Rejection paths.
    for label, text in (
        ("empty", ""),
        ("no_objective",
         "## Required Commands\n```bash\nmake ci\n```\nStop.\n"),
        ("no_stop",
         "## Objective\nDo a thing.\n"),
        ("placeholder_only_deliverable",
         "## Objective\nDo a thing.\n## Required Outputs\n- TODO\nStop.\n"),
        ("protected_and_mutable_overlap",
         "## Objective\nx\n## Do Not Modify\n- vectors/**\n## May Modify\n- vectors/**\nStop.\n"),
    ):
        try:
            parse_work_order(text)
            expect(f"rejects_{label}", False, "did not raise")
        except WorkOrderError:
            expect(f"rejects_{label}", True)

    if failures:
        print(f"\nFAIL: {len(failures)} self-check failures")
        for f in failures:
            print(f"  ↳ {f}")
        return 1
    print("\nPASS: work_order_parser self-check")
    return 0


if __name__ == "__main__":
    raise SystemExit(self_check())
