# Results

## The five-Bond coordination farce

The canonical assignment set of {{RESULT_ASSIGNMENTS}} orders across the
{{CONFIG_NUM_AGENTS}}-agent roster produces {{RESULT_OVERLAP_COUNT}} overlaps
and {{RESULT_CONFLICT_COUNT}} conflicts. Three Bonds crowd the baccarat
table; Vesper and Jimmy both infiltrate SMERSH headquarters; and Cooper's
order to burn the baccarat table conflicts with the three agents assigned to
win the championship on that same table. A single clearance violation is
recorded (Jimmy, clearance 2, sent to an operation requiring 4).

![Per-task agent load; bars above the dashed line are overlaps.](../output/figures/coordination_farce.png){#fig:coordination}

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
of **{{RESULT_CHAOS_INDEX}}**. All five protocol rules fire at least once:
two exclusive-task rejections, two clearance failures, two double-bookings,
one duplicate order, and one duplicate-codename rejection.

![Dispatch timeline: accepted orders vs protocol violations per tick.](../output/figures/dispatch_chaos.png){#fig:dispatch}

The dominant failure mode is identity collapse: because all five agents share
the codename *James Bond*, the dispatch centre repeatedly mistakes one agent
for another and misroutes the under-cleared nephew onto cleared operations.

## Spoof ops doctrine

The film's standing orders of {{RESULT_DIRECTIVES}} directives score a
**spoof index of {{RESULT_SPOOF_INDEX}} / 100**, with a mean per-directive
score of {{RESULT_MEAN_SPOOF_SCORE}}. The worst offender is
*"{{RESULT_WORST_DIRECTIVE}}"* — an inversion of the proportionality principle.

![Per-directive spoof scores with the aggregate index in the title.](../output/figures/spoof_analyzer.png){#fig:spoof}

Contradiction detection attributes the scores across the sane rule surface
(identity, single-agent discipline, command, discretion, force, fratricide),
demonstrating that the analyzer exercises every rule rather than a narrow
subset.
