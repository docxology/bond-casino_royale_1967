# Methodology

## 1. The coordination-farce model

`src/casino_royale_1967/coordination_farce.py` models the organizational
failure behind *Casino Royale*. The model has three parts: a static roster,
an assignment set, and an analysis function.

**Roster.** A tuple of {{CONFIG_NUM_AGENTS}} `Agent` instances, each with an
id, the actor who played them (David Niven, Peter Sellers, Ursula Andress,
Woody Allen, Terence Cooper), a clearance level (1–5), a jurisdiction, and a
codename. Crucially, **all five share the codename `James Bond`** — the
roster is a duplicate-identity dataset by construction.

**Tasks.** A `Task` catalog of {{CONFIG_NUM_TASKS}} operations drawn from the
film's plot, each with a required clearance and an exclusivity flag. Tasks
include winning the baccarat championship, infiltrating SMERSH headquarters,
guarding the casino vault, seducing Mata Bond, disabling the gamma-ray
projector, and burning the baccarat table for the insurance claim.
Mutually exclusive task pairs are captured in a conflict graph: *win the
baccarat championship* conflicts with *burn the baccarat table*.

**Analysis** (`analyze_assignments`). Given a tuple of `Assignment`s
(agent, task, priority), the function deterministically computes:

- **Overlap count** — every extra distinct agent beyond the first on a task.
  A task with three Bonds contributes two overlaps.
- **Conflict count** — every unordered pair of distinct agents assigned to a
  conflicting task pair.
- **Clearance violations** — assignments where the agent's clearance is below
  the task's requirement (reported, not counted twice in the loss).
- **Coordination loss** — a weighted sum
  `loss = overlap_weight * overlap_count + conflict_weight * conflict_count`,
  with weights {{CONFIG_OVERLAP_WEIGHT}} and {{CONFIG_CONFLICT_WEIGHT}}.

The canonical default `DEFAULT_ASSIGNMENTS` assigns {{RESULT_ASSIGNMENTS}}
orders and produces the farce documented in the results: three Bonds at the
baccarat table, Cooper burning the same table, Vesper and Jimmy both at
SMERSH headquarters.

**Remedy** (`deduplicate_assignments`). Single-agent discipline keeps the
highest-priority assignment per task (ties broken by lexicographic agent id)
and retires the overlap victims. Applied to the canonical farce it keeps
{{RESULT_DEDUP_KEPT}} assignments and drops {{RESULT_DEDUP_DROPPED}},
eliminating every overlap and every duplicate-agent conflict. Only one
irreducible clash remains: a single agent must still win the baccarat
championship while a second burns the same table for the insurance claim, so
one conflict (loss equal to the conflict weight) persists.

## 2. The dispatch-chaos simulation

`src/casino_royale_1967/dispatch_chaos.py` simulates a dispatch centre that
cannot tell its agents apart. It is a tick-based, priority-ordered scheduler
with no randomness and no wall clock.

**Orders.** Each `DispatchOrder` names an order id, agent, task, priority, and
issue tick. Orders are processed in `issued_tick` order; within a tick, higher
priority first, ties broken by order id. State is deterministic: agents
committed to a task persist across ticks (task occupancy), and agents
committed to a task within the current tick are re-checked for double-booking.

**Protocol rules.** Five rules are enforced per order, in this order:

1. `duplicate_order` — an order id issued twice is rejected;
2. `exclusive_task` — an exclusive task may hold only one agent;
3. `clearance` — the agent's clearance must meet the task requirement;
4. `double_booking` — one agent may not take two tasks in the same tick;
5. `duplicate_codename` — if another agent with the *same codename* already
   occupies a task, the order is rejected (the dispatch centre mistakes the
   Bonds for one another).

A rejected order is dropped, never requeued: chaotic dispatch loses orders.

**Output.** `simulate_dispatch` returns a `DispatchReport` with total,
dispatched, and rejected counts, every `DispatchViolation` with the rule that
fired, the success ratio, and a chaos index equal to
`violations / total_orders`, normalised to `[0, 1]`. The canonical scenario
issues {{RESULT_ORDERS}} orders across {{CONFIG_MAX_TICKS}} ticks.

## 3. The spoof protocol analyzer

`src/casino_royale_1967/spoof_analyzer.py` measures how far a satirical ops
doctrine deviates from a sane protocol. It combines lexical marker scoring,
rule-contradiction detection, and oxymoron detection.

**Sane doctrine.** `REAL_OPS_RULES` lists six rules (classified identity,
single point of command, covert discretion, proportional force, no
fratricide, single agent per operation). The analyzer treats these as the
ground truth the farce inverts.

**Markers.** `SPOOF_MARKERS` weights absolutist or inverted vocabulary
(`every`, `anyone`, `all`, `none`, `maximum`, `in case of doubt`,
`blow up`, `shoot`, `identical`, `never`, `always`). Matching is
word-boundary aware so `any` does not fire inside `anyone` and `all` does not
fire inside `calling`.

**Scoring.** For each directive, `analyze_doctrine` computes:

- the **marker score** — the sum of weights of markers present;
- **inverted rules** — real rules whose keyword appears together with an
  absolutist marker, i.e. a discretionary rule turned absolute;
- **oxymorons** — self-contradicting phrase pairs from `OXYMORON_PAIRS`
  (classified + publicity, discreet + explosion, ...).

The per-directive score is
`marker_sum + 2.0 * len(inverted_rules) + 1.5 * len(oxymorons)`. The
aggregate **spoof index** is the mean score scaled to `[0, 100]`
(`min(100, mean * 10)`), rounded to one decimal. The film's canonical
standing orders comprise {{RESULT_DIRECTIVES}} directives.
