# Standalone Package Guide — FIVE 00s

**Casino Royale (1967): FIVE 00s** is a PROJECT BOND film package. It is a
**local-only** working tree inside the BOND suite
(`projects/working/bond/casino_royale_1967`) — there is no remote and it is
never pushed. This guide documents what the package is, its boundaries, and
how to verify it.

## Purpose

FIVE 00s implements deterministic mission software for the 1967 *Casino
Royale* farce: a five-agent coordination-failure model, a dispatch-chaos
simulation, and a spoof-protocol analyzer, exposed through the FROZEN
`bond_api` `MissionProvider` protocol.

## Dependency / isolation

- Pure domain core (`coordination_farce.py`, `dispatch_chaos.py`,
  `spoof_analyzer.py`): stdlib + numpy only, **no** `infrastructure.*` and
  **no** `bond_api` imports — importable standalone.
- `mission.py`: the single thin adapter that imports the frozen `bond_api`
  protocol types. `pyproject.toml` binds `bond-api` via
  `[tool.uv.sources] bond-api = { path = "..." }`.
- No template `infrastructure.*` imports anywhere (`layer_contract.yaml`
  declares an empty allow-list).

## Verification (run from the package root)

```bash
uv sync --extra dev
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ && uv run ruff format --check src/ scripts/
uv run mypy src/ scripts/
```

## Regenerate artifacts

```bash
uv run python scripts/mission.py execute   # deterministic mission outcome
uv run python scripts/mission.py figures   # the three concept figures
uv run python scripts/z_generate_manuscript_variables.py  # tokens + resolved tree
```

`output/` is git-ignored and regenerable; the tree stays clean after re-runs.

## What not to claim

- No published DOI / external repository: the package is local-only. Do not
  add Zenodo/GitHub location fields to the sidecars.
- The "chaos index" and "spoof index" are deterministic, satirical
  diagnostics for the film's plot — not validated real-world governance
  metrics.
