"""Pytest configuration: deterministic backend + import paths.

* ``MPLBACKEND=Agg`` so matplotlib never opens a display window.
* Project root and ``src/`` on ``sys.path`` so ``casino_royale_1967`` and the
  installed ``bond_api`` resolve regardless of the invocation directory.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
for _path in (_PROJECT_ROOT, _PROJECT_ROOT / "src"):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))
