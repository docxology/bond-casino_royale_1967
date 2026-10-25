# Standalone Package Guide — FIVE 00s

**Casino Royale (1967): FIVE 00s** is a PROJECT BOND film package, drafted as
a working tree inside the BOND suite
(`projects/working/bond/casino_royale_1967`) and tracked at
`github.com/docxology/bond-casino_royale_1967`. This guide documents what the
package is, its boundaries, and how to verify it.

## Purpose

FIVE 00s implements deterministic mission software for the 1967 *Casino
Royale* farce, exposed through the FROZEN `bond_api` `MissionProvider`
protocol. Six domain modules, one per concept:

| Module | Concept |
|---|---|
| `coordination_farce.py` | five-agent roster, overlap/conflict/clearance analysis, single-agent deduplication |
| `dispatch_chaos.py` | tick-based dispatch simulation under five protocol rules |
| `spoof_analyzer.py` | lexical scoring of the satirical ops doctrine |
| `identity_confusion.py` | information theory + Bayes over the shared codename |
| `baccarat_table.py` | chemin de fer deal odds and the table-collision metric |
| `escalation_ladder.py` | doctrine as an absorbing Markov chain |

Plus `figures/plots.py` (six deterministic figures), `manuscript_variables.py`
(live `{{TOKEN}}` hydration) and `mission.py` (the single `bond_api` adapter).

## Dependency / isolation

- Pure domain core — all six modules above plus `figures/plots.py`: stdlib +
  numpy + matplotlib + pyyaml only, **no** `infrastructure.*` and **no**
  `bond_api` imports, so they are importable standalone.
  `tests/test_layer_contract.py` proves this in a subprocess with `bond_api`
  blocked at the meta-path level, and carries a positive control asserting
  `mission.py` *does* fail under the same conditions.
- `mission.py`: the single thin adapter that imports the frozen `bond_api`
  protocol types. `pyproject.toml` binds `bond-api` via
  `[tool.uv.sources] bond-api = { path = "..." }`.
- `manuscript_variables.py`: token hydration plus the strict writer. It reads
  `CODENAME`, `IDENTITY` and `PACKAGE_VERSION` from the adapter at import
  time, so it needs `bond_api` importable as well — it is deliberately outside
  `DOMAIN_MODULES` in `tests/test_layer_contract.py`.
- No template `infrastructure.*` imports anywhere (`layer_contract.yaml`
  declares an empty allow-list).

## Verification (run from the package root)

```bash
uv sync --all-extras
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/
```

## Regenerate artifacts

```bash
uv run python scripts/mission.py execute   # deterministic mission outcome
uv run python scripts/mission.py figures   # the six concept figures
uv run python scripts/z_generate_manuscript_variables.py  # tokens + figures + resolved tree
```

`output/` is git-ignored and regenerable; the tree stays clean after re-runs.

## What not to claim

- No published DOI: the package is not registered with Zenodo, so no DOI
  belongs in the sidecars. The repository itself is
  `github.com/docxology/bond-casino_royale_1967`, recorded in `CITATION.cff`
  and `codemeta.json`.
- The "chaos index" and "spoof index" are deterministic, satirical
  diagnostics for the film's plot — not validated real-world governance
  metrics.
- The five-Bond hand-collision probability is computed under an
  i.i.d.-across-hands approximation (exact within a hand, independent across
  hands). It is not the exact without-replacement figure — see `TODO.md`.
- `deal_outcome_probabilities` is an infinite-deck (with-replacement)
  computation. It says nothing about finite-deck or single-deck play.
