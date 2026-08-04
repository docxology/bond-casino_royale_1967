# Testing Philosophy — FIVE 00s

## Zero-mock policy

Every test in `tests/` exercises **real computation and real protocol types**.
No `MagicMock`, `@patch`, `mocker.patch`, or `create_autospec`. The
deterministic providers and the installed `bond_api` protocol are the real
artifacts under test.

## What is covered

| File | Covers |
|---|---|
| `test_coordination_farce.py` | roster/catalog facts, overlap + conflict + clearance detection, weighted loss, deduplication semantics, error branches |
| `test_dispatch_chaos.py` | all five protocol rules, canonical counts/ratios, determinism, validation errors |
| `test_spoof_analyzer.py` | word-boundary scoring, rule contradictance, oxymorons, aggregate index, robustness (empty / bare-string input) |
| `test_mission.py` | `bond_api` protocol conformance, five-stage flow, determinism, gadget registry, serialization round-trips, slug discovery |
| `test_manuscript_variables.py` | token map, config loading, strict resolved-tree writer, the **live cross-reference gate** over `manuscript/[0-9]*.md` |
| `test_scripts_smoke.py` | subprocess runs of the thin CLIs (exit codes + parsed output) |
| `test_figures.py` | deterministic PNG render + byte-idempotence |

## Coverage mechanics

> The canonical gate (from the package directory):
> `uv run pytest tests/ --cov=src --cov-fail-under=90`

Coverage is measured on `src/` only (test code excluded), line + branch,
with a `fail_under` of 90. All tests use fixed, deterministic inputs. The
suite targets full coverage of the domain core and the protocol adapter; any
uncovered branch should be intentional and driven out by a real-data test.
