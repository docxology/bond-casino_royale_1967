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
intended) — {{RESULT_IDENTITY_MI}} bits of mutual information in absolute
terms. Two distinct conditional entropies follow from that, and they are not
interchangeable [@cover2006elements]:

| Direction | Reading | Bits |
|---|---|---|
| `H(routed \| intended)` | knowing who the order was *for*, how uncertain its destination is | {{RESULT_IDENTITY_AMBIGUITY}} |
| `H(intended \| routed)` | seeing where the order *landed*, how uncertain its author's intent is | {{RESULT_IDENTITY_RESIDUAL}} |

The first subtracts the mutual information from the routing entropy
({{RESULT_IDENTITY_ROUTING_ENTROPY}} bits); the second subtracts it from the
prior entropy of the intended identity
({{RESULT_IDENTITY_PRIOR_ENTROPY}} bits). This manuscript reports the first as
the **dispatch ambiguity**; the phrase "bits of identity lost per dispatch"
refers to that forward direction and must not be computed as
prior minus mutual information, which yields the second, larger figure.
A Bayesian sighting (jurisdiction match + clearance sufficiency) at
the SMERSH operation resolves to *{{RESULT_IDENTITY_RESOLUTION}}* with
posterior confidence {{RESULT_IDENTITY_CONFIDENCE}}.

![Routing confusion matrix across the five Bonds.](../output/figures/{{FIGURE_IDENTITY}}){#fig:identity}

## The casino table

The baccarat table model derives the deal odds under the standard
chemin de fer drawing rules: **player {{RESULT_BACCARAT_PLAYER}}, banker
{{RESULT_BACCARAT_BANKER}}, tie {{RESULT_BACCARAT_TIE}}** (a banker advantage
of {{RESULT_BANKER_ADVANTAGE}}) — the canonical infinite-deck figures
[@ethier2010doctrine], exact for the with-replacement model the enumeration
implements.

The farce lives at the table itself: with all {{CONFIG_TABLE_BONDS}} Bonds
seated, the probability that at least two are dealt the same hand total is
**{{RESULT_TABLE_COLLISION}}** — a hand-collision farce more likely than not.
That figure is not exact. Each Bond's two-card total is drawn from the exact
no-replacement distribution of a single hand, but the five hands are then
combined as if independent, whereas in a real deal they compete for the same
shoe. The number is therefore the collision probability *under the
i.i.d.-across-hands approximation* the code documents, and
`tests/test_baccarat_table.py` exhibits a small deck on which that
approximation is measurably wrong — it is a modelling assumption, not a
rounding detail. Its magnitude for a full standard shoe is not quantified
here; `TODO.md` records that gap as an accepted, open limitation.

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

