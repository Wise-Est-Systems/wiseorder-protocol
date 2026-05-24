#!/usr/bin/env python3
"""Triple-implementation canonicalization sweep.

Generates a stream of candidate JSON inputs, canonicalizes each through the
Python, Go, and Rust tracks, and diffs the results. Agreements are recorded
as lock-candidates; disagreements are recorded as bug reports with the exact
bytes that drove them apart.

Operates only against scratch directories and the new `canonicalize`
subcommand on each verifier. Does NOT touch SPEC.md, vectors/, schemas/, or
canonicalization/corpus/.

Output:
  reports/triple_sweep/<timestamp>/
    inputs/             every generated input (.json)
    results.jsonl       one line per input: agreement matrix
    agreements.jsonl    subset where all three agreed
    disagreements.jsonl subset where any pair disagreed
    summary.json        totals, generator breakdown, timing
    thermal.log         periodic pmset thermal readings

Safe-max envelope:
  - parallelism capped (--workers, default 6 on 10-core M4)
  - per-call timeout (default 30s)
  - thermal poll every 60s; halt on any pmset warning > 0
  - inputs written to a scratch directory under reports/triple_sweep/<ts>/

Usage:
  triple_sweep.py [--count N] [--workers W] [--seed S] [--timeout T]
                  [--no-rust] [--no-go]

Exit codes:
  0  sweep completed (may include disagreements; see summary.json)
  1  sweep aborted (thermal halt, subprocess failure, etc.)
  2  usage error
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import math
import random
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = REPO_ROOT / "reports" / "triple_sweep"


_UNICODE_EDGE_CODEPOINTS = [
    0x0000,
    0x0007,
    0x001F,
    0x0020,
    0x007F,
    0x0080,
    0x00FF,
    0x0100,
    0x07FF,
    0x0800,
    0xFEFF,
    0xFFFD,
    0xFFFF,
    0x10000,
    0x1F600,
    0x10FFFF,
    0x003C,
    0x003E,
    0x0026,
    0x002F,
    0x0022,
    0x005C,
    0x2028,
    0x2029,
]
_UNICODE_EDGE_CHARS = [chr(cp) for cp in _UNICODE_EDGE_CODEPOINTS]

_NUMBER_EDGES = [
    0,
    -0,
    1,
    -1,
    2**31 - 1,
    -(2**31),
    2**53 - 1,
    2**53,
    2**53 + 1,
    2**63 - 1,
    -(2**63),
    2**64,
    0.0,
    -0.0,
    0.1,
    0.2,
    0.3,
    0.1 + 0.2,
    1.0 / 3.0,
    1.7976931348623157e308,
    2.2250738585072014e-308,
    5e-324,
    math.pi,
    math.e,
    -2.5,
    3.14159,
    0.001,
    1e10,
    1e15,
    1e16,
    1e17,
    1e100,
    1e-100,
]


def gen_unicode_string(rng: random.Random) -> Any:
    n = rng.randint(1, 8)
    return "".join(rng.choice(_UNICODE_EDGE_CHARS) for _ in range(n))


def gen_object_unicode_keys(rng: random.Random) -> Any:
    n = rng.randint(2, 6)
    out: dict[str, Any] = {}
    for _ in range(n):
        k = gen_unicode_string(rng)
        out[k] = rng.randint(-1000, 1000)
    return out


def gen_number_edge(rng: random.Random) -> Any:
    return rng.choice(_NUMBER_EDGES)


def gen_mixed_object(rng: random.Random) -> Any:
    keys = [f"k{i}" for i in range(rng.randint(1, 6))]
    rng.shuffle(keys)
    out: dict[str, Any] = {}
    for k in keys:
        choice = rng.randint(0, 5)
        if choice == 0:
            out[k] = gen_number_edge(rng)
        elif choice == 1:
            out[k] = gen_unicode_string(rng)
        elif choice == 2:
            out[k] = rng.choice([True, False, None])
        elif choice == 3:
            out[k] = [gen_number_edge(rng) for _ in range(rng.randint(0, 4))]
        elif choice == 4:
            out[k] = {f"nk{i}": gen_number_edge(rng) for i in range(rng.randint(0, 3))}
        else:
            out[k] = []
    return out


def gen_nested(rng: random.Random) -> Any:
    depth = rng.randint(2, 5)
    cur: Any = gen_number_edge(rng)
    for _ in range(depth):
        if rng.random() < 0.5:
            cur = {gen_unicode_string(rng): cur, "tag": rng.randint(0, 9)}
        else:
            cur = [cur, gen_number_edge(rng), gen_unicode_string(rng)]
    return cur


def gen_array_order(rng: random.Random) -> Any:
    n = rng.randint(2, 8)
    items: list[Any] = []
    for _ in range(n):
        items.append(
            rng.choice(
                [
                    rng.randint(-100, 100),
                    gen_unicode_string(rng),
                    gen_number_edge(rng),
                ]
            )
        )
    return items


def gen_whitespace_key(rng: random.Random) -> Any:
    return {
        " ": 1,
        "  ": 2,
        "\t": 3,
        "\n": 4,
        "a b": 5,
        "a\tb": 6,
    }


def gen_duplicate_like_keys(rng: random.Random) -> Any:
    return {
        "key": 1,
        "Key": 2,
        "KEY": 3,
        "kéy": 4,
        "kéy": 5,
    }


GENERATORS: dict[str, Callable[[random.Random], Any]] = {
    "number_edge": gen_number_edge,
    "unicode_string": gen_unicode_string,
    "object_unicode_keys": gen_object_unicode_keys,
    "mixed_object": gen_mixed_object,
    "nested": gen_nested,
    "array_order": gen_array_order,
    "whitespace_key": gen_whitespace_key,
    "duplicate_like_keys": gen_duplicate_like_keys,
}


def generate_inputs(count: int, rng: random.Random) -> Iterable[tuple[str, Any]]:
    names = list(GENERATORS.keys())
    for i in range(count):
        name = names[i % len(names)]
        yield name, GENERATORS[name](rng)


@dataclasses.dataclass
class CanonResult:
    impl: str
    ok: bool
    canonical_b64: str = ""
    sha256_hex: str = ""
    length: int = 0
    error: str = ""


def _run_subprocess(label: str, real_cmd: list[str], timeout: float) -> CanonResult:
    try:
        proc = subprocess.run(
            real_cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return CanonResult(impl=label, ok=False, error="timeout")
    except OSError as exc:
        return CanonResult(impl=label, ok=False, error=f"oserror:{exc}")
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout).strip()
        return CanonResult(impl=label, ok=False, error=f"exit{proc.returncode}:{err[:200]}")
    stdout = proc.stdout.strip().splitlines()
    if not stdout:
        return CanonResult(impl=label, ok=False, error="empty-stdout")
    line = stdout[-1]
    try:
        report = json.loads(line)
    except json.JSONDecodeError as exc:
        return CanonResult(impl=label, ok=False, error=f"bad-json:{exc}")
    return CanonResult(
        impl=label,
        ok=True,
        canonical_b64=str(report.get("canonical_b64", "")),
        sha256_hex=str(report.get("sha256_hex", "")),
        length=int(report.get("length", -1)),
    )


def run_python(input_path: Path, timeout: float, python_bin: str) -> CanonResult:
    return _run_subprocess(
        "python",
        [python_bin, str(REPO_ROOT / "tools" / "canonicalize_cli.py"), str(input_path)],
        timeout,
    )


def run_go(input_path: Path, timeout: float, go_bin: Path | None) -> CanonResult:
    if go_bin is not None and go_bin.exists():
        return _run_subprocess("go", [str(go_bin), "canonicalize", str(input_path)], timeout)
    return _run_subprocess(
        "go",
        ["go", "run", "./go_verifier", "canonicalize", str(input_path)],
        timeout,
    )


def run_rust(input_path: Path, timeout: float, rust_bin: Path | None) -> CanonResult:
    if rust_bin is not None and rust_bin.exists():
        return _run_subprocess("rust", [str(rust_bin), "canonicalize", str(input_path)], timeout)
    return _run_subprocess(
        "rust",
        [
            "cargo",
            "run",
            "--manifest-path",
            str(REPO_ROOT / "rust_verifier" / "Cargo.toml"),
            "--quiet",
            "--release",
            "--",
            "canonicalize",
            str(input_path),
        ],
        timeout,
    )


class ThermalGuard:
    def __init__(self, log_path: Path, interval_s: float = 60.0) -> None:
        self.log_path = log_path
        self.interval_s = interval_s
        self._last_poll = 0.0
        self.halted = False
        self.last_reading: dict[str, Any] = {}

    def poll(self, force: bool = False) -> None:
        now = time.time()
        if not force and (now - self._last_poll) < self.interval_s:
            return
        self._last_poll = now
        try:
            proc = subprocess.run(
                ["pmset", "-g", "therm"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            output = proc.stdout
        except (OSError, subprocess.TimeoutExpired) as exc:
            output = f"<pmset failed: {exc}>"
        reading = {"ts": _now_iso(), "output": output.strip()}
        self.last_reading = reading
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(reading) + "\n")
        lower = output.lower()
        if "warning level" in lower:
            for line in output.splitlines():
                if "warning level" in line.lower() and "=" in line:
                    tail = line.split("=", 1)[-1].strip()
                    if tail.isdigit() and int(tail) > 0:
                        self.halted = True
                        return


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ensure_python_bin() -> str:
    venv_py = REPO_ROOT / ".venv" / "bin" / "python"
    if venv_py.exists():
        return str(venv_py)
    return sys.executable


def _maybe_prebuild_rust() -> Path | None:
    proc = subprocess.run(
        [
            "cargo",
            "build",
            "--quiet",
            "--release",
            "--manifest-path",
            str(REPO_ROOT / "rust_verifier" / "Cargo.toml"),
        ],
        capture_output=True,
        text=True,
        timeout=900,
    )
    if proc.returncode != 0:
        print("warning: rust prebuild failed:", proc.stderr.strip(), file=sys.stderr)
        return None
    bin_path = REPO_ROOT / "rust_verifier" / "target" / "release" / "rust_verifier"
    return bin_path if bin_path.exists() else None


def _maybe_prebuild_go() -> Path | None:
    out_dir = REPO_ROOT / "go_verifier" / "target"
    out_dir.mkdir(parents=True, exist_ok=True)
    bin_path = out_dir / "go_verifier"
    proc = subprocess.run(
        ["go", "build", "-o", str(bin_path), "./go_verifier"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=300,
    )
    if proc.returncode != 0:
        print("warning: go prebuild failed:", proc.stderr.strip(), file=sys.stderr)
        return None
    return bin_path if bin_path.exists() else None


def _input_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--count", type=int, default=100)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--seed", type=int, default=0xC0FFEE)
    ap.add_argument("--timeout", type=float, default=30.0)
    ap.add_argument("--no-go", action="store_true")
    ap.add_argument("--no-rust", action="store_true")
    ap.add_argument("--thermal-interval", type=float, default=60.0)
    args = ap.parse_args(argv)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = REPORTS_DIR / ts
    inputs_dir = run_dir / "inputs"
    inputs_dir.mkdir(parents=True, exist_ok=True)

    results_path = run_dir / "results.jsonl"
    agreements_path = run_dir / "agreements.jsonl"
    disagreements_path = run_dir / "disagreements.jsonl"
    summary_path = run_dir / "summary.json"
    thermal_path = run_dir / "thermal.log"

    python_bin = _ensure_python_bin()
    print(f"[triple_sweep] run dir: {run_dir}", file=sys.stderr)

    rust_bin: Path | None = None
    go_bin: Path | None = None
    if not args.no_rust:
        print("[triple_sweep] prebuilding rust verifier (release)...", file=sys.stderr)
        rust_bin = _maybe_prebuild_rust()
        if rust_bin:
            print(f"[triple_sweep] rust binary: {rust_bin}", file=sys.stderr)
    if not args.no_go:
        print("[triple_sweep] prebuilding go verifier...", file=sys.stderr)
        go_bin = _maybe_prebuild_go()
        if go_bin:
            print(f"[triple_sweep] go binary: {go_bin}", file=sys.stderr)

    guard = ThermalGuard(thermal_path, interval_s=args.thermal_interval)
    guard.poll(force=True)
    if guard.halted:
        print("[triple_sweep] HALT: thermal warning before start", file=sys.stderr)
        return 1

    rng = random.Random(args.seed)
    inputs: list[tuple[str, Any, Path]] = []
    for i, (gen_name, value) in enumerate(generate_inputs(args.count, rng)):
        ih = _input_hash(value)
        path = inputs_dir / f"{i:06d}-{gen_name}-{ih}.json"
        try:
            with path.open("w", encoding="utf-8") as fh:
                json.dump(value, fh, ensure_ascii=False)
        except (OSError, TypeError, ValueError) as exc:
            print(f"warning: skipping unserializable input {i}: {exc}", file=sys.stderr)
            continue
        inputs.append((gen_name, value, path))

    print(f"[triple_sweep] inputs prepared: {len(inputs)}", file=sys.stderr)

    def run_one(input_path: Path) -> dict[str, CanonResult]:
        out: dict[str, CanonResult] = {}
        out["python"] = run_python(input_path, args.timeout, python_bin)
        if not args.no_go:
            out["go"] = run_go(input_path, args.timeout, go_bin)
        if not args.no_rust:
            out["rust"] = run_rust(input_path, args.timeout, rust_bin)
        return out

    started = time.time()
    total = 0
    agreements = 0
    disagreements = 0
    errors = 0
    by_generator: dict[str, dict[str, int]] = {}

    results_fh = results_path.open("w", encoding="utf-8")
    agree_fh = agreements_path.open("w", encoding="utf-8")
    disagree_fh = disagreements_path.open("w", encoding="utf-8")

    try:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            future_to_meta = {
                pool.submit(run_one, path): (gen_name, value, path)
                for (gen_name, value, path) in inputs
            }
            for fut in as_completed(future_to_meta):
                gen_name, value, path = future_to_meta[fut]
                total += 1
                try:
                    impls = fut.result()
                except Exception as exc:  # noqa: BLE001
                    impls = {"harness": CanonResult(impl="harness", ok=False, error=str(exc))}

                ok_results = [r for r in impls.values() if r.ok]
                err_results = [r for r in impls.values() if not r.ok]
                if err_results:
                    errors += 1

                shas = {r.sha256_hex for r in ok_results}
                b64s = {r.canonical_b64 for r in ok_results}
                lens = {r.length for r in ok_results}
                agreed = (
                    not err_results
                    and len(impls) >= 2
                    and len(shas) == 1
                    and len(b64s) == 1
                    and len(lens) == 1
                )

                rec = {
                    "input_path": str(path.relative_to(REPO_ROOT)),
                    "generator": gen_name,
                    "input_value": value,
                    "agreed": agreed,
                    "results": {k: dataclasses.asdict(v) for k, v in impls.items()},
                }
                results_fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                if agreed:
                    agreements += 1
                    agree_fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                else:
                    disagreements += 1
                    disagree_fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

                bucket = by_generator.setdefault(
                    gen_name,
                    {"total": 0, "agreed": 0, "disagreed": 0, "errors": 0},
                )
                bucket["total"] += 1
                bucket["agreed" if agreed else "disagreed"] += 1
                if err_results:
                    bucket["errors"] += 1

                if total % 25 == 0:
                    elapsed = time.time() - started
                    print(
                        f"[triple_sweep] {total}/{len(inputs)} "
                        f"agree={agreements} disagree={disagreements} err={errors} "
                        f"({elapsed:.1f}s)",
                        file=sys.stderr,
                    )

                guard.poll()
                if guard.halted:
                    print("[triple_sweep] HALT: thermal warning, draining workers", file=sys.stderr)
                    for f in future_to_meta:
                        f.cancel()
                    break
    finally:
        results_fh.close()
        agree_fh.close()
        disagree_fh.close()

    elapsed = time.time() - started
    summary = {
        "ts": ts,
        "count_requested": args.count,
        "count_processed": total,
        "agreements": agreements,
        "disagreements": disagreements,
        "errors": errors,
        "elapsed_seconds": round(elapsed, 3),
        "workers": args.workers,
        "seed": args.seed,
        "timeout": args.timeout,
        "tracks": {
            "python": True,
            "go": not args.no_go,
            "rust": not args.no_rust,
        },
        "by_generator": by_generator,
        "halted_thermal": guard.halted,
        "last_thermal_reading": guard.last_reading,
        "run_dir": str(run_dir.relative_to(REPO_ROOT)),
    }
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2), file=sys.stderr)
    return 1 if guard.halted else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
