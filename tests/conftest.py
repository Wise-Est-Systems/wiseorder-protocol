"""Pytest setup: make tools/, interop/scripts/, and intellagent_runtime importable."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Order matters: REPO must come first so `import intellagent_runtime.X` resolves
# to the package directory under the repo root.
for path in (REPO, REPO / "tools", REPO / "interop" / "scripts"):
    s = str(path)
    if s not in sys.path:
        sys.path.insert(0, s)
