---
name: casino-royale-1967
description: PROJECT BOND film package — Casino Royale (1967) FIVE 00s: coordination-failure model, dispatch-chaos simulation, spoof protocol analyzer, bond_api MissionProvider.
version: 1.0.0
author: bond
license: MIT
tags: [bond, film-package, multi-agent-coordination, deterministic, bond-api]
---

# casino-royale-1967

Project-scoped skill for the FIVE 00s package at
`projects/working/bond/casino_royale_1967/`. Load when working inside the
package.

## When to Use

- Working inside the `casino_royale_1967` package — running scripts, editing
  the domain core, or regenerating artifacts.
- Extending any of the three concepts (coordination-farce model,
  dispatch-chaos simulation, spoof protocol analyzer).
- Implementing/verifying the `bond_api` `MissionProvider` adapter, gadgets,
  or the manuscript-token pipeline.

## Quick Reference

```bash
# From the package root
uv sync --extra dev
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ && uv run ruff format --check src/ scripts/
uv run mypy src/ scripts/

uv run python scripts/mission.py execute     # deterministic mission outcome
uv run python scripts/mission.py figures     # three concept figures
uv run python scripts/z_generate_manuscript_variables.py  # tokens + resolved tree
```

## Module map

| Module | Role |
|---|---|
| `src/casino_royale_1967/coordination_farce.py` | Five-Bond overlap/conflict/clearance analysis + dedup |
| `src/casino_royale_1967/dispatch_chaos.py` | Tick-based dispatch simulator (5 protocol rules) |
| `src/casino_royale_1967/spoof_analyzer.py` | Satirical doctrine scorer + spoof index |
| `src/casino_royale_1967/mission.py` | The only `bond_api` adapter (`MissionProvider`, gadgets) |
| `src/casino_royale_1967/manuscript_variables.py` | Live `{{TOKEN}}` hydration + strict resolver |
| `src/casino_royale_1967/figures/plots.py` | Deterministic PNG figures |

## Pitfalls

- **Domain core stays pure.** `coordination_farce.py`, `dispatch_chaos.py`,
  `spoof_analyzer.py`, and `figures/` must never import `infrastructure.*` or
  `bond_api` — only `mission.py` adapts to the frozen protocol.
- **No mocks.** All tests use real computation + real `bond_api` types.
- **Determinism.** Domain artifacts must be byte-reproducible (seed 7, no
  wall clock). The only wall-clock value is the `GENERATION_TIMESTAMP` token.
- **Metrics injected, never hand-authored.** Reference manuscript numbers as
  `{{TOKEN}}`s; the live cross-reference test enforces completeness.
- **`uv sync --extra dev` before pytest** after any pyproject change (the
  `bond-api` path dependency must resolve).
- **Outputs are disposable.** Never hand-edit `output/` — regenerate.
- **Run from the package root**, not the template root.

## Cross-refs

- Package contract: [`../../../AGENTS.md`](../../../AGENTS.md)
- README: [`../../../README.md`](../../../README.md)
- TODO: [`../../../TODO.md`](../../../TODO.md)
