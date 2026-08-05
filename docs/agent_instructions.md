# Agent Instructions — Casino Royale (1967) · FIVE 00s

Read this before modifying any file in
`projects/working/bond/casino_royale_1967/`. These are hard constraints, not
suggestions.

## Rule 1 — Scope is exactly this package

Work only inside this package directory. Do not touch sibling BOND packages,
bond root files, or the template repo. The tree is **local-only** — there is no
remote and nothing is ever pushed. Commit inside this repo only.

## Rule 2 — Zero mocks

No `unittest.mock`, `MagicMock`, `mocker.patch`, or `create_autospec` anywhere
in `tests/`. Tests must exercise real computation with real data and real
`bond_api` protocol types. A deterministic provider that implements the real
protocol is not a mock. If you need to exercise a missing dependency, do it for
real — a `sys.meta_path` finder in a subprocess, as `test_layer_contract.py`
does.

## Rule 3 — Thin orchestrators in `scripts/`

`scripts/` is glue: `sys.path` bootstrap plus argument forwarding and output
formatting. All business logic lives in `src/casino_royale_1967/`. Never
implement math or construct a protocol type in a script.

## Rule 4 — Metrics are injected, never hand-authored

Any measured number in the manuscript must arrive as a `{{TOKEN}}` from
`manuscript/config.yaml` + `src/casino_royale_1967/manuscript_variables.py`.
Three gates in `tests/test_manuscript_variables.py` enforce this: an unknown
token fails, a generated-but-unused token fails, and a bare numeral in
`03_results.md` or `04_conclusion.md` fails.

If you state a new quantitative result, add the variable first and reference
the token second. Never the other way round.

## Rule 5 — Determinism

Domain artifacts must be byte-reproducible: no RNG in any analysis, no wall
clock in any domain report. The only wall-clock value is the
`GENERATION_TIMESTAMP` token, overridable via `now=` in tests. Seed 7 is the
mission's declared provenance identity, not an RNG state.

## Rule 6 — The layer contract

The six pure domain modules — `coordination_farce.py`, `dispatch_chaos.py`,
`spoof_analyzer.py`, `identity_confusion.py`, `baccarat_table.py`,
`escalation_ladder.py` — plus `figures/plots.py` must import **stdlib + numpy
+ matplotlib only**. No `infrastructure.*`. No `bond_api`.

`mission.py` is the only module that may import `bond_api`, and the package
`__init__.py` resolves its exports lazily so the core stays importable without
it. `tests/test_layer_contract.py` enforces both halves; if you add a domain
module, add it to that test's `DOMAIN_MODULES` (its completeness check fails
until you do).

## Rule 7 — Never change the frozen protocol surface

`bond-cli`, the coordinator's reconcile, and the orchestrator consume these
symbols across all 33 packages. Do not rename, re-signature, or remove:

- `MissionProvider` with `film = "casino_royale_1967"`;
- `brief()`, `recon(request)`, `plan(brief)`, `execute(plan)`,
  `debrief(outcome)`;
- `GADGETS`, `GADGET_REGISTRY`, `register_gadgets(registry=None)`.

Deepen *inside* these stages — richer payloads, more findings, more plan steps,
new gadget entries. Never alter their shape.

## Rule 8 — Gate before reporting done

```bash
uv sync --extra dev
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ && uv run ruff format --check src/ scripts/
uv run mypy src/ scripts/
grep -rn "unittest.mock\|MagicMock\|@patch\|create_autospec" tests/ || echo Clean
rg -n "template[_]code_project" . --glob '!uv.lock' --glob '!.git/**' || echo Clean
git status --short   # must be clean after your commit
```

`uv` cannot write its cache under a restrictive sandbox. If a command fails
with `Failed to initialize cache`, that is an environment restriction, not a
package failure — re-run it with the sandbox disabled.

## Rule 9 — Regenerate artifacts, never hand-edit them

`output/` is disposable and regenerable. After changing anything that affects a
metric or a figure:

```bash
uv run python scripts/z_generate_manuscript_variables.py
```

This recomputes the token map, re-renders every figure, and rewrites
`output/manuscript/` with all markers resolved, failing loudly if any token is
unresolvable. Never edit a file under `output/` to make a gate pass.

## Rule 10 — Build the failing case first

When you add a gate, assertion, or invariant check, write the input that should
break it and confirm that it does. A check that cannot fail is worse than no
check, because it reports safety it does not provide. See the positive controls
in [testing_philosophy.md](testing_philosophy.md).
