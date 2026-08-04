# Introduction

The 1967 film *Casino Royale* is not one Bond but many. Sir James Bond
(played by David Niven) is recalled from retirement; the would-be successor
is a baccarat prodigy (Peter Sellers as Evelyn Tremble); a Soviet defector
(Ursula Andress as Vesper Lynd) doubles as a double-0; and James Bond's
anxious nephew (Woody Allen as Jimmy Bond) and a field agent (Terence Cooper)
both answer to the same codename. Every operative introduces themselves as
**James Bond**. The result is a coordination catastrophe dressed as a
blockbuster: overlapping identities, overlapping assignments, and directly
contradictory orders.

**FIVE 00s** turns that farce into a rigorous, deterministic model. This
manuscript documents three complementary concepts, each implemented in pure
Python with no mocks and verified by real computation:

- **Multi-agent coordination failure** — overlap and conflict detection over
  a roster of five overlapping Bonds, with a weighted loss and a
  single-agent remedy.
- **Agent dispatch chaos** — a tick-based simulation in which the dispatch
  centre cannot tell its Bonds apart, so protocol violations accumulate.
- **Spoof protocol analysis** — automatic measurement of how far a satirical
  ops doctrine (the film's standing orders) deviates from a sane protocol.

The whole package is wired into the PROJECT BOND suite: a `MissionProvider`
(`src/casino_royale_1967/mission.py`) implements the frozen `bond_api`
protocol, the five mission phases are exposed as thin CLIs under `scripts/`,
and manuscript figures are generated deterministically from the same analyses
the mission executes. Metrics in this manuscript are never hand-authored —
they are injected live from `manuscript/config.yaml` and
`src/casino_royale_1967/manuscript_variables.py`.

## Reader's guide

- **Methodology** describes the three algorithms: assignment analysis,
  tick-based dispatch, and lexical doctrine scoring.
- **Results** reports the canonical metrics and the three figures.
- **Experimental setup** lists the configuration parameters.
- **Reproducibility** describes how every artifact can be regenerated
  byte-identically.
