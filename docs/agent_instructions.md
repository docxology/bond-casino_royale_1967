# Agent Instructions — FIVE 00s

Read this before modifying any file in
`projects/working/bond/casino_royale_1967/`. These are hard constraints, not
suggestions.

## Rule 1 — Scope is exactly this package

Work only inside this package directory. Do not touch sibling BOND packages,
bond root files, or the template repo. The tree is **local-only** — never
push, there is no remote.

## Rule 2 — Zero mocks

No `unittest.mock`, `MagicMock`, `mocker.patch`, or `create_autospec`
anywhere in `tests/`. Tests must exercise real computation with real data and
real `bond_api` protocol types. A deterministic provider that implements the
real protocol is not a mock.

## Rule 3 — Thin orchestrators in scripts/

`scripts/` is glue: sys.path bootstrap + argument forwarding. All business
logic lives in `src/casino_royale_1967/`. Never implement math or protocol
construction in a script.

## Rule 4 — Metrics are injected, never hand-authored

Any numeric result in the manuscript must come from `manuscript/config.yaml`
+ `src/casino_royale_1967/manuscript_variables.py` via `{{TOKEN}}`
substitution. Do not hardcode a measured number in prose.

## Rule 5 — Determinism

Domain artifacts must be byte-reproducible: fixed seed 7, no untracked RNG,
no wall clock in domain reports. The only wall-clock value is the
`GENERATION_TIMESTAMP` token, overridable in tests.

## Rule 6 — Layer contract

The pure domain modules (`coordination_farce.py`, `dispatch_chaos.py`,
`spoof_analyzer.py`, `figures/`) must not import `infrastructure.*` or
`bond_api`. Only `mission.py` adapts the domain core to the FROZEN `bond_api`
protocol.

## Rule 7 — Gate before done

Run the full verification before reporting done:

```bash
uv sync --extra dev
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ && uv run ruff format src/ scripts/
uv run mypy src/ scripts/
rg -n "template[_]code_project" . --glob '!uv.lock' --glob '!.git/**' || echo Clean
git status --short
```

Commit with a path-scoped message inside this repo only.
