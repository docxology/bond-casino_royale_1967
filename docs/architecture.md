# Architecture — FIVE 00s

## Layers

```
scripts/ (thin CLIs)
   |
   v
src/casino_royale_1967/mission.py        <- the only bond_api adapter
   |
   v
src/casino_royale_1967/{coordination_farce, dispatch_chaos, spoof_analyzer}.py   <- pure core
src/casino_royale_1967/manuscript_variables.py                                  <- token hydration
src/casino_royale_1967/figures/plots.py                                         <- deterministic PNGs
```

Dependencies flow one way. Nothing imports `infrastructure.*`. Only
`mission.py` imports `bond_api`.

## The six concepts

1. **coordination_farce.py** — `Agent` / `Task` / `Assignment` dataclasses,
   the five-Bond `AGENT_ROSTER` and `TASK_CATALOG`, `analyze_assignments`
   (overlap / conflict / clearance / weighted loss) and
   `deduplicate_assignments` (single-agent discipline).
2. **dispatch_chaos.py** — `DispatchOrder`, `simulate_dispatch` (tick-based,
   priority-ordered, five rule checks), `DispatchReport` / `DispatchViolation`
   / `DispatchEvent`.
3. **spoof_analyzer.py** — `REAL_OPS_RULES`, `SPOOF_MARKERS`,
   `OXYMORON_PAIRS`, `CANONICAL_SPOOF_DOCTRINE`, `analyze_doctrine`
   (marker + inversion + oxymoron scoring, normalised spoof index).
4. **identity_confusion.py** — feature-vector softmax confusion matrix,
   Shannon entropy / mutual information / NMI, and Bayesian sighting
   resolution (`analyze_identity`, `resolve_identity`).
5. **baccarat_table.py** — hand valuation, draw rules, exact infinite-deck
   deal odds, and the birthday-bound `hand_collision_probability`.
6. **escalation_ladder.py** — absorbing Markov chain: fundamental matrix,
   expected absorption times, spectral radius, `compare_doctrines`.

## How to add a concept

1. Create the pure module in `src/casino_royale_1967/` (stdlib + numpy only,
   deterministic, fully typed, documented).
2. Add a real-data test file `tests/test_<module>.py`.
3. Wire the concept into `mission.py` (a plan step + a results payload) and,
   if it has a figure, add a `render_*_figure` in `figures/plots.py`.
4. Add any new manuscript tokens to
   `src/casino_royale_1967/manuscript_variables.py` and reference them with
   `{{TOKEN}}` in a `manuscript/[0-9]*.md` section (the live cross-reference
   test enforces this).
5. Re-run the full gate.

## Forbidden patterns

- No `infrastructure.*` imports anywhere in `src/`.
- No mock framework in `tests/`.
- No business logic inside `scripts/`.
- No hard-coded measured numbers in the manuscript.
