# Testing Philosophy — Casino Royale (1967) · FIVE 00s

Why the tests in this package look the way they do, and what a new test has to
do to belong here.

## Zero-mock policy

No `unittest.mock`, `MagicMock`, `@patch`, `mocker.patch`, or
`create_autospec` anywhere in `tests/`. Every test exercises **real
computation on real data**. The five-Bond roster, the task catalog, the chaos
order stream, the spoof doctrine, the 52-card deck composition and the doctrine
transition matrices are all genuine declared domain data, and the installed
`bond_api` protocol types are the real artifacts under test.

A deterministic provider that implements the real protocol is *not* a mock —
it is the production object. Where a test needs to exercise an absent
dependency (`tests/test_layer_contract.py` blocking `bond_api`), it does so
with a real `sys.meta_path` finder raising a real `ModuleNotFoundError` in a
real subprocess, not by patching an import.

## Determinism

Nothing in the domain core draws a random number, so there is no seed to fix
inside an analysis; the declared seed 7 lives in `Provenance` as the mission's
identity, not as an RNG state. The only wall-clock value in the whole system is
the `GENERATION_TIMESTAMP` manuscript token, and every test that touches the
token map passes an explicit `now=` so its output is fixed.

Consequences a test may rely on and must preserve:

- `simulate_dispatch()` is a pure function of its order stream.
- `compare_doctrines() == compare_doctrines()`.
- Figures re-render byte-identically (`tests/test_figures.py` asserts this).
- `brief → recon → plan → execute → debrief` is byte-reproducible, and
  `_input_fingerprint()` is a stable sha256 over the canonical inputs.

## What each test file covers

| File | Covers |
|---|---|
| `test_coordination_farce.py` | roster/catalog facts, overlap + conflict + clearance detection, distinct-agent conflict semantics, weighted loss, deduplication and its tie-break, error branches |
| `test_dispatch_chaos.py` | all five protocol rules (bound to `PROTOCOL_RULES` itself), canonical counts and ratios, the default order stream, determinism, validation errors |
| `test_spoof_analyzer.py` | word-boundary marker scoring, rule contradiction, oxymorons, the aggregate index, robustness on empty and bare-string input |
| `test_identity_confusion.py` | entropy functions, confusion-matrix row-stochasticity, NMI, Bayesian resolution, degenerate single-agent edge cases |
| `test_baccarat_table.py` | hand/draw rules including an exhaustive sweep of the banque table, canonical odds cross-validated against an independent brute force, the hand-collision bound, error branches |
| `test_escalation_ladder.py` | validation, fundamental matrix, expected absorption, the matrix-derived absorbing set (reversed-ladder and multi-absorbing regressions), spectral radius under complex eigenvalues |
| `test_layer_contract.py` | the domain core imports without `bond_api` (subprocess + positive control), no forbidden imports in any domain module, lazy adapter exports |
| `test_mission.py` | `bond_api` protocol conformance, the five-stage flow, determinism, the gadget registry, serialization round-trips, slug discovery |
| `test_manuscript_variables.py` | the token map, config loading, the strict resolved-tree writer, and three manuscript gates (below) |
| `test_scripts_smoke.py` | subprocess runs of the thin CLIs — exit codes and parsed output |
| `test_figures.py` | deterministic PNG render plus byte-idempotence |

## The three manuscript gates

Prose drifting away from code is the failure mode this package guards hardest
against, because a manuscript number is the least likely thing anyone
re-derives.

1. **Unknown tokens fail.** Every `{{TOKEN}}` appearing in
   `manuscript/[0-9]*.md` must exist in the generated token map — the same
   strict check the renderer performs.
2. **Unused tokens fail.** Every generated token must be referenced by some
   section. This gate exists because six `FIGURE_*` tokens were once generated
   and never used while the manuscript hardcoded PNG filenames, so a rename in
   `FIGURE_FILENAMES` would have silently broken every image link.
3. **Bare numerals in results prose fail.** `03_results.md` and
   `04_conclusion.md` may not contain a numeral outside a token, apart from a
   short documented allowlist (the `/100` scale denominator, the film's year,
   and the declared coverage floor). Methodology and setup are exempt because
   their numerals are *definitions* — card values, drawing rules, loss-weight
   formulas — not measurements.

## Positive controls

A gate that cannot fail is worse than no gate, because it reports safety it
does not provide. Several checks here therefore ship with an explicit
counter-test:

- the `bond_api`-blocking probe is re-run against `mission.py`, which **must**
  fail — otherwise a broken blocker would make the layer-contract test pass for
  the wrong reason;
- the numeral scanner is asserted against injected literals
  (`"the loss is 15."` — the sentence-final case an earlier regex missed);
- the domain-module scan asserts its own scan set matches what is on disk, so
  it cannot quietly cover nothing;
- `test_every_rule_fires` compares against `PROTOCOL_RULES` itself rather than
  a hand-copied list, so adding a sixth rule cannot leave the test green.

Write new gates the same way: build the failing case first, and check that it
fails.

## Coverage mechanics

The canonical gate, run from the package directory:

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
```

Coverage is measured on `src/` only (test code excluded), **line and branch**,
with `fail_under = 90`. Package `__init__.py` files are omitted per
`pyproject.toml`, so the lazy re-export shim is exercised by
`test_layer_contract.py` rather than counted.

The floor is 90%; the suite currently sits well above it. Quote the floor, not
the measurement — a figure pasted into prose goes stale the moment a line
moves, and `docs/` is not regenerated. Run the gate if you want the current
number.

An uncovered branch is a finding, not a rounding error: it usually means either
a missing real-data test or genuinely unreachable code that should be deleted.
The dead `return False` at the end of `banker_should_draw` was found exactly
this way and removed, with an exhaustive domain sweep added in its place.
