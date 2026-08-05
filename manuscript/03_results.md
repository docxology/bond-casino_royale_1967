# Results

## The five-Bond coordination farce

The canonical assignment set of {{RESULT_ASSIGNMENTS}} orders across the
{{CONFIG_NUM_AGENTS}}-agent roster produces {{RESULT_OVERLAP_COUNT}} overlaps
and {{RESULT_CONFLICT_COUNT}} conflicts. Three Bonds crowd the baccarat
table; Vesper and Jimmy both infiltrate SMERSH headquarters; and Cooper's
order to burn the baccarat table conflicts with the three agents assigned to
win the championship on that same table. Conflicts are counted between
*distinct* agents only, so an operative holding both sides of a mutually
exclusive pair is a scheduling problem rather than a conflict.
{{RESULT_CLEARANCE_VIOLATIONS}} clearance violation is recorded:
`{{RESULT_CLEARANCE_AGENT}}` ({{RESULT_CLEARANCE_ALIAS}}), clearance
{{RESULT_CLEARANCE_LEVEL}}, sent to *{{RESULT_CLEARANCE_TASK}}* — an
operation requiring clearance {{RESULT_CLEARANCE_REQUIRED}}.

![Per-task agent load; bars above the dashed line are overlaps.](../output/figures/{{FIGURE_COORDINATION}}){#fig:coordination}

The weighted **coordination loss** is **{{RESULT_COORDINATION_LOSS}}**
(weights {{CONFIG_OVERLAP_WEIGHT}} for overlap and
{{CONFIG_CONFLICT_WEIGHT}} for conflict). Applying single-agent discipline
keeps {{RESULT_DEDUP_KEPT}} of the {{RESULT_ASSIGNMENTS}} assignments and
drops {{RESULT_DEDUP_DROPPED}}, eliminating every overlap; only the
irreducible clash between winning and burning the baccarat table remains, at
one conflict (loss {{CONFIG_CONFLICT_WEIGHT}}).

## Dispatch chaos

The dispatch simulator issues {{RESULT_ORDERS}} orders; {{RESULT_DISPATCHED}}
dispatch successfully and {{RESULT_REJECTED}} are rejected as protocol
violations, for a success ratio of {{RESULT_SUCCESS_RATIO}} and a chaos index
of **{{RESULT_CHAOS_INDEX}}**. All {{CONFIG_PROTOCOL_RULES}} protocol rules
fire at least once ({{RESULT_RULES_FIRED}} of {{CONFIG_PROTOCOL_RULES}}
distinct rules triggered), so the scenario is a positive control for the whole
rule set rather than a narrow subset:

| Protocol rule | Rejections |
|---|---|
| `exclusive_task` | {{RESULT_RULE_EXCLUSIVE_TASK}} |
| `clearance` | {{RESULT_RULE_CLEARANCE}} |
| `double_booking` | {{RESULT_RULE_DOUBLE_BOOKING}} |
| `duplicate_order` | {{RESULT_RULE_DUPLICATE_ORDER}} |
| `duplicate_codename` | {{RESULT_RULE_DUPLICATE_CODENAME}} |

![Dispatch timeline: accepted orders vs protocol violations per tick.](../output/figures/{{FIGURE_DISPATCH}}){#fig:dispatch}

The dominant failure mode is identity collapse: because all five agents share
the codename *James Bond*, the dispatch centre repeatedly mistakes one agent
for another and misroutes the under-cleared nephew onto cleared operations.

## Spoof ops doctrine

The film's standing orders of {{RESULT_DIRECTIVES}} directives score a
**spoof index of {{RESULT_SPOOF_INDEX}} / 100**, with a mean per-directive
score of {{RESULT_MEAN_SPOOF_SCORE}}. The worst offender is
*"{{RESULT_WORST_DIRECTIVE}}"* — an inversion of the proportionality principle.

![Per-directive spoof scores with the aggregate index in the title.](../output/figures/{{FIGURE_SPOOF}}){#fig:spoof}

Contradiction detection attributes the scores across the sane rule surface
(identity, single-agent discipline, command, discretion, force, fratricide):
{{RESULT_DOCTRINE_RULES_HIT}} of the {{CONFIG_DOCTRINE_RULES}} declared rules
are contradicted at least once, so the analyzer exercises every rule rather
than a narrow subset.

## Identity confusion

The five Bonds share one codename, and the resulting identity collapse is
measured in bits. Routing carries only
**{{RESULT_IDENTITY_NMI}} normalized mutual information** (a near-zero value:
the observed routing reveals almost nothing about which physical Bond was
intended), while each dispatch loses **{{RESULT_IDENTITY_AMBIGUITY}} bits** of
identity. In absolute terms the intended identity carries
{{RESULT_IDENTITY_PRIOR_ENTROPY}} bits and routing recovers only
{{RESULT_IDENTITY_MI}} bits of it. A Bayesian sighting
(jurisdiction match + clearance sufficiency) at
the SMERSH operation resolves to *{{RESULT_IDENTITY_RESOLUTION}}* with
posterior confidence {{RESULT_IDENTITY_CONFIDENCE}}.

![Routing confusion matrix across the five Bonds.](../output/figures/{{FIGURE_IDENTITY}}){#fig:identity}

## The casino table

The baccarat table model derives the exact deal odds under the standard
chemin de fer drawing rules: **player {{RESULT_BACCARAT_PLAYER}}, banker
{{RESULT_BACCARAT_BANKER}}, tie {{RESULT_BACCARAT_TIE}}** (a banker advantage
of {{RESULT_BANKER_ADVANTAGE}}) — the canonical infinite-deck figures. The
farce lives at the table itself: with all {{CONFIG_TABLE_BONDS}} Bonds seated,
the probability that at least two are dealt the same hand total is
**{{RESULT_TABLE_COLLISION}}** — a hand-collision farce more likely than not.

![Casino table deal odds with the five-Bond collision probability.](../output/figures/{{FIGURE_BACCARAT}}){#fig:baccarat}

## Escalation ladder

Modelled as an absorbing Markov chain over the
{{CONFIG_LADDER_STATES}}-state ladder
`quiet → rumour → scandal → spectacle → catastrophe`, the spoof doctrine
reaches catastrophe in **{{RESULT_ESCALATION_SPOOF}} expected steps**, while a
disciplined doctrine takes {{RESULT_ESCALATION_SANCTIONED}} — the farce
escalates **{{RESULT_ESCALATION_ACCELERATION}}× faster**.

Absorption is certain rather than assumed: the transient block of the spoof
doctrine has spectral radius {{RESULT_ESCALATION_SPECTRAL}} (strictly below
one), and the absorption probability into
*{{RESULT_ESCALATION_ABSORBING_STATE}}* from `quiet` is
{{RESULT_ESCALATION_ABSORPTION}}. The absorbing set is derived from the
transition matrix itself — a row with a unit diagonal and no outflow — never
from a state's name, so relabelling or reordering the ladder cannot change the
analysis.

![Expected steps to catastrophe per state, by doctrine.](../output/figures/{{FIGURE_ESCALATION}}){#fig:escalation}

