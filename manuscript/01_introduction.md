# Introduction

The 1967 film *Casino Royale* [@casinoroyale1967film] is not one Bond but many. Sir James Bond
(played by David Niven) is recalled from retirement; the would-be successor
is a baccarat prodigy (Peter Sellers as Evelyn Tremble); a Soviet defector
(Ursula Andress as Vesper Lynd) doubles as a double-0; and James Bond's
anxious nephew (Woody Allen as Jimmy Bond) and a field agent (Terence Cooper)
both answer to the same codename. Every operative introduces themselves as
**James Bond**. The result is a coordination catastrophe dressed as a
blockbuster: overlapping identities, overlapping assignments, and directly
contradictory orders.

**FIVE 00s** turns that farce into a rigorous, deterministic model. This
manuscript documents six complementary concepts, each implemented as a pure
Python module with no mocks and verified by real computation:

- **Multi-agent coordination failure** (`coordination_farce.py`) — overlap and
  conflict detection over a roster of {{CONFIG_NUM_AGENTS}} overlapping Bonds
  across {{CONFIG_NUM_TASKS}} tasks, with a weighted loss and a single-agent
  remedy.
- **Agent dispatch chaos** (`dispatch_chaos.py`) — a tick-based simulation in
  which the dispatch centre cannot tell its Bonds apart, so violations of
  {{CONFIG_PROTOCOL_RULES}} protocol rules accumulate.
- **Spoof protocol analysis** (`spoof_analyzer.py`) — automatic measurement of
  how far a satirical ops doctrine (the film's standing orders) deviates from
  a sane protocol of {{CONFIG_DOCTRINE_RULES}} rules.
- **Identity confusion** (`identity_confusion.py`) — information theory
  [@shannon1948communication] over the shared codename: a routing confusion matrix, entropy, mutual
  information, and Bayesian resolution of a dispatch sighting.
- **The baccarat table** (`baccarat_table.py`) — exact chemin de fer deal odds
  by enumeration, plus the birthday-model probability that two of the
  {{CONFIG_TABLE_BONDS}} Bonds at the table are dealt the same hand total.
- **The escalation ladder** (`escalation_ladder.py`) — doctrine as an
  absorbing Markov chain over {{CONFIG_LADDER_STATES}} states, compared
  against a disciplined doctrine through expected absorption times.

The whole package is wired into the PROJECT BOND suite: a `MissionProvider`
(`src/casino_royale_1967/mission.py`) implements the frozen `bond_api`
protocol, the five mission phases are exposed as thin CLIs under `scripts/`,
and {{CONFIG_NUM_FIGURES}} manuscript figures are generated deterministically
from the same analyses the mission executes. Metrics in this manuscript are
never hand-authored — they are injected live from `manuscript/config.yaml` and
`src/casino_royale_1967/manuscript_variables.py`.

## Reader's guide

- **Methodology** describes the six algorithms in module order: assignment
  analysis, tick-based dispatch, lexical doctrine scoring, the
  information-theoretic identity model, exact baccarat enumeration, and the
  absorbing-chain escalation ladder.
- **Results** reports the canonical metrics and the {{CONFIG_NUM_FIGURES}}
  figures.
- **Experimental setup** lists the configuration parameters.
- **Reproducibility** describes how every artifact can be regenerated
  byte-identically.
- **Scope and related work** states what the models deliberately do not claim.
