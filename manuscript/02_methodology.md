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

## 4. The identity-confusion model

`src/casino_royale_1967/identity_confusion.py` quantifies the codename
collapse with information theory and Bayesian inference.

**Confusion matrix.** Each agent is represented by a feature vector
(normalized clearance + a jurisdiction one-hot over the task catalog).
Routing confusion `confusion[i][j]` — the probability an order intended for
agent *i* is routed to agent *j* — is a row-softmax over pairwise feature
similarity scaled by a temperature. The matrix is row-stochastic and
deterministic.

**Entropy / mutual information.** With a uniform prior over the five Bonds,
the model computes Shannon entropy of the intended identity
`H(intended)` ({{RESULT_IDENTITY_NMI}}-related), the conditional entropy
`H(routed | intended)` — its **identity ambiguity** of
{{RESULT_IDENTITY_AMBIGUITY}} bits — the marginal routing entropy, the mutual
information `I = H(routed) - H(routed|intended)`, and the normalized mutual
information `NMI = I / max(H(intended), H(routed))`. Because all five agents
share one codename, the *codename* itself carries `0` bits; the shared name
is pure identity loss.

**Bayesian resolution.** Given a dispatch sighting's evidence — whether the
presented jurisdiction matched the task's and whether clearance was
sufficient — `resolve_identity` computes the posterior over the roster with a
uniform prior and an independent jurisdiction/clearance likelihood table. The
argmax is the resolution, its mass the confidence.

## 5. The baccarat table model

`src/casino_royale_1967/baccarat_table.py` models the casino set-piece with
exact enumeration.

**Hand valuation.** Baccarat hands total modulo 10; 10/J/Q/K count as 0;
a two-card total of 8 or 9 is a *natural* that ends the deal immediately.
The player draws on 0-5 and stands on 6-7; the banker follows the standard
chemin de fer table keyed on its total and the player's third card.

**Deal odds.** `deal_outcome_probabilities` enumerates every draw outcome
(four to six cards) under the drawing rules, weighting each card by its
value's share of the deck — the industry-standard infinite-deck baccarat odds
computation. For the 52-card standard it reproduces the canonical published
figures (player {{RESULT_BACCARAT_PLAYER}}, banker {{RESULT_BACCARAT_BANKER}},
tie {{RESULT_BACCARAT_TIE}}), with the banker's historical advantage of
{{RESULT_BANKER_ADVANTAGE}}.

**The farce metric.** `two_card_total_counts` computes the *exact*
no-replacement marginal distribution of a two-card hand total from the actual
deck; `hand_collision_probability` then applies the birthday bound — the
elementary symmetric polynomial `n! * e_n(p_0..p_9)` — to answer: across
{{CONFIG_TABLE_BONDS}} Bonds at the table, what is the probability at least
two are dealt the same hand total? The answer is {{RESULT_TABLE_COLLISION}}.

## 6. The escalation-ladder model

`src/casino_royale_1967/escalation_ladder.py` models doctrine as an absorbing
Markov chain (Kemeny-Snell analysis, exact numpy linear algebra).

The ladder `quiet → rumour → scandal → spectacle → catastrophe` has
`catastrophe` absorbing. A doctrine is a row-stochastic transition matrix
(`SPOOF_DOCTRINE_TRANSITIONS`, `SANCTIONED_DOCTRINE_TRANSITIONS`). The
analysis computes:

- the **fundamental matrix** `N = (I - Q)^{-1}` over the transient states;
- the **expected absorption time** `t = N @ 1` from each state — the expected
  steps to catastrophe;
- a **spectral radius** of `Q` below 1 (guaranteeing absorption) and the
  absorption probability (~1.0).

`compare_doctrines` reports the **escalation index** (expected steps from
`quiet`) under each doctrine and the acceleration factor
`sanctioned / spoof`: the farce reaches catastrophe in
{{RESULT_ESCALATION_SPOOF}} steps versus {{RESULT_ESCALATION_SANCTIONED}}
under discretion — {{RESULT_ESCALATION_ACCELERATION}}× faster.

