# docs/ — Casino Royale (1967) · FIVE 00s

Documentation for the FIVE 00s package: deterministic mission software for the
1967 *Casino Royale* farce in which five operatives all answer to the codename
*James Bond*, exposed through the FROZEN `bond_api` mission protocol.

## What is in this directory

| File | What it holds |
|---|---|
| [README.md](README.md) | This index — what the docs cover and where the code lives |
| [AGENTS.md](AGENTS.md) | How an agent should work inside this package: reading order and the checks that matter |
| [agent_instructions.md](agent_instructions.md) | The ten hard operational rules — scope, zero-mock, thin orchestrators, injected metrics, determinism, layer contract, frozen protocol, the gate, artifact regeneration, positive controls |
| [architecture.md](architecture.md) | Module-by-module architecture of `src/`, how the pieces compose, and how `mission.py` implements the frozen `MissionProvider` |
| [testing_philosophy.md](testing_philosophy.md) | The no-mock / real-data / determinism doctrine as it applies here, the three manuscript gates, and the positive controls behind them |

Package-level docs live one directory up: [`../README.md`](../README.md)
(what the package is), [`../AGENTS.md`](../AGENTS.md) (the package spec), and
[`../TODO.md`](../TODO.md) (remaining work and integration points).

## Where the code lives

### Domain core — pure, `bond_api`-free, stdlib + numpy only

| Path | Computes |
|---|---|
| `src/casino_royale_1967/coordination_farce.py` | The five-Bond roster, task catalog and conflict graph; overlap / conflict / clearance analysis with a weighted loss, plus the single-agent deduplication remedy |
| `src/casino_royale_1967/dispatch_chaos.py` | A tick-based dispatch simulation enforcing five protocol rules, producing violations, a chaos index and an event timeline |
| `src/casino_royale_1967/spoof_analyzer.py` | Lexical scoring of satirical ops doctrine against six sane rules — markers, rule inversions, oxymorons, and a normalised spoof index |
| `src/casino_royale_1967/identity_confusion.py` | Softmax routing confusion matrix; entropy, conditional entropy, mutual information and NMI; Bayesian resolution of a dispatch sighting |
| `src/casino_royale_1967/baccarat_table.py` | Chemin de fer hand and draw rules, exact enumerated deal odds, and the birthday-bound hand-collision probability across the seated Bonds |
| `src/casino_royale_1967/escalation_ladder.py` | Doctrine as an absorbing Markov chain — fundamental matrix, expected absorption times, spectral radius, spoof-vs-sanctioned comparison |

### Adapter, generation and orchestration

| Path | Role |
|---|---|
| `src/casino_royale_1967/mission.py` | The single `bond_api` adapter: `MissionProvider` (brief/recon/plan/execute/debrief), `GADGETS`, `GADGET_REGISTRY`, `register_gadgets` |
| `src/casino_royale_1967/manuscript_variables.py` | Live `{{TOKEN}}` hydration from config + domain core, and the strict resolved-manuscript writer |
| `src/casino_royale_1967/figures/plots.py` | Six deterministic matplotlib figures, one per concept |
| `scripts/mission.py` | Thin CLIs for the five mission phases plus `figures` |
| `scripts/z_generate_manuscript_variables.py` | Thin CLI: token map + figures + resolved manuscript tree |
| `manuscript/` | The FIVE 00s manuscript (nine numbered sections, config, preamble, bibliography) |
| `tests/` | Per-module real-data tests plus protocol, layer-contract, manuscript, figure and CLI-smoke suites |

## Quick start

```bash
uv sync --extra dev
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run python scripts/mission.py execute
uv run python scripts/z_generate_manuscript_variables.py
```

`uv` cannot write its cache under a restrictive sandbox; a `Failed to
initialize cache` error is an environment restriction, not a package failure.
