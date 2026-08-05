#!/usr/bin/env python3
"""Thin orchestrator: generate and inject FIVE 00s manuscript variables.

Computes the ``{{TOKEN}}`` map from ``manuscript/config.yaml`` plus the live
deterministic domain metrics (``src/.../manuscript_variables.py``), writes
``output/data/manuscript_variables.json``, renders all six concept figures
into ``output/figures/``, and resolves every ``{{TOKEN}}`` into
``output/manuscript/*.md`` for PDF rendering.

Substitution is strict: an unresolvable token raises rather than leaving a
marker in the rendered output.

Exit codes:
    0   variables written and injected successfully
    1   unexpected error
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "src"))  # noqa: E402
sys.path.insert(0, str(_PROJECT_ROOT))  # noqa: E402

from casino_royale_1967.figures.plots import render_all_figures  # noqa: E402
from casino_royale_1967.manuscript_variables import (  # noqa: E402
    generate_variables,
    save_variables,
    write_resolved_manuscript_tree,
)


def main() -> int:
    variables = generate_variables(_PROJECT_ROOT)
    out_path = _PROJECT_ROOT / "output" / "data" / "manuscript_variables.json"
    save_variables(variables, out_path)
    render_all_figures(_PROJECT_ROOT / "output" / "figures")
    write_resolved_manuscript_tree(_PROJECT_ROOT, variables)
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
