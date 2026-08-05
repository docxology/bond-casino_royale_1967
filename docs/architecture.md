# Architecture — Casino Royale (1967) · FIVE 00s

How this package is put together: what each module in `src/` computes, how the
pieces compose, and how `mission.py` implements the frozen `bond_api`
`MissionProvider`.

## Layer topology

Dependencies flow strictly downward. Nothing in `src/` imports
`infrastructure.*` at all, and exactly one module imports `bond_api`.

```
scripts/mission.py                    scripts/z_generate_manuscript_variables.py
      |  (argv forwarding only)              |  (argv forwarding only)
      v                                      v
src/casino_royale_1967/mission.py      src/casino_royale_1967/manuscript_variables.py
      |  <- the ONLY bond_api adapter        |  <- token hydration + strict writer
      |                                      |
      +--------------------+-----------------+
                           v
   src/casino_royale_1967/  (pure domain core: stdlib + numpy only)
     coordination_farce.py   dispatch_chaos.py     spoof_analyzer.py
     identity_confusion.py   baccarat_table.py     escalation_ladder.py
     figures/plots.py        (matplotlib, Agg backend)
```

`src/casino_royale_1967/__init__.py` re-exports the domain core eagerly and the
adapter symbols **lazily** (PEP 562 module `__getattr__`), so importing a
domain module never pulls in `bond_api`. `tests/test_layer_contract.py` proves
this by importing the whole core in a subprocess with `bond_api` blocked at the
meta-path level — and carries a positive control asserting `mission.py` *does*
fail under the same conditions, so the test cannot pass vacuously.

## The six domain modules

Each is deterministic (no RNG, no wall clock), fully typed, and covered by its
own real-data test file.

### 1. `coordination_farce.py` — who is stepping on whom

The film's premise as data, plus one analysis function.

- **Data**: `AGENT_ROSTER` (five `Agent`s — id, the actor who played them,
  clearance 1–5, jurisdiction, and the codename *James Bond* they all share),
  `TASK_CATALOG` (six `Task`s with a required clearance and an exclusivity
  flag), `CONFLICT_GRAPH` (mutually exclusive task pairs), and
  `DEFAULT_ASSIGNMENTS` (the canonical farce).
- **`analyze_assignments`** returns a `CoordinationReport`: the **overlap
  count** (extra distinct agents beyond the first on each task), the
  **conflict count** (pairs of *distinct* agents across a conflicting task
  pair — an agent holding both sides counts for nothing), **clearance
  violations**, per-task load, overlap victims, and the weighted
  **coordination loss** `overlap_weight * overlaps + conflict_weight *
  conflicts`.
- **`deduplicate_assignments`** is the remedy: keep the lexicographic maximum
  of `(priority, agent_id)` per task, so the result is a pure function of the
  assignment *set* rather than of its ordering. It retires exactly the agents
  `analyze_assignments` names as `overlap_victims` — both call the shared
  `_winner_by_task`, and a test asserts `overlap_victims == dropped_by_task`
  task for task. (Before that helper existed the victims were "everyone after
  the lexicographically first id", which named a different Bond than the one
  deduplication actually dropped, while three documents claimed they matched.)

Every other domain module depends on this one for the roster and catalog.

### 2. `dispatch_chaos.py` — orders lost to identity collapse

A tick-based, priority-ordered dispatch scheduler with no randomness.
`simulate_dispatch` walks the order stream and applies `PROTOCOL_RULES` in a
fixed precedence: `duplicate_order`, `exclusive_task`, `clearance`,
`double_booking`, `duplicate_codename`. It returns a `DispatchReport` with
accepted/rejected counts, every `DispatchViolation` tagged with the rule that
fired, the success ratio, a chaos index (`violations / total_orders`), and a
tick-by-tick `DispatchEvent` timeline for the figure.

This is a **reject model**: a rejected order is dropped, never requeued, so
`mean_delay` is always `0.0`. That is the chaotic-dispatch premise, not an
oversight — see `TODO.md` for the queueing variant as future work.

### 3. `spoof_analyzer.py` — measuring how far doctrine has drifted

Lexical scoring of a satirical ops doctrine against `REAL_OPS_RULES` (six sane
rules). `analyze_doctrine` scores each directive as
`marker_sum + 2.0 * len(inverted_rules) + 1.5 * len(oxymorons)`, where markers
are matched with word boundaries (`any` must not fire inside `anyone`), a rule
is *inverted* when its keyword co-occurs with an absolutist marker, and
oxymorons come from `OXYMORON_PAIRS`. The aggregate **spoof index** is the mean
score scaled to `[0, 100]`.

### 4. `identity_confusion.py` — the codename collapse in bits

Information theory over the shared codename.

- **`build_confusion_matrix`** — a row-softmax over pairwise similarity of
  agent feature vectors (normalized clearance concatenated with a one-hot over
  the roster's *distinct jurisdictions*, not the task catalog). Row-stochastic
  and deterministic. The codename contributes no feature at all, because it is
  identical for everyone — which is exactly the point.
- **`entropy` / `conditional_entropy` / `residual_identity_entropy` /
  `mutual_information` / `normalized_mutual_information`** — `H(intended)`;
  the forward *dispatch ambiguity* `H(routed | intended)`; the reverse
  residual `H(intended | routed) = H(intended) - I`; the mutual information
  `I = H(routed) - H(routed | intended)`; and `NMI` normalized by
  `max(H(intended), H(routed))`. The two conditional entropies are separate
  functions and separate report fields because they are different numbers —
  subtracting `I` from the prior does **not** give the dispatch ambiguity.
- **`resolve_identity`** — a Bayesian posterior over the roster from a
  sighting's `(jurisdiction_match, clearance_ok)` evidence, using a documented
  likelihood table; the argmax is the resolution and its mass the confidence.
- **`analyze_identity`** bundles all of it into a frozen `IdentityReport`.

### 5. `baccarat_table.py` — the odds at the table everyone showed up to

- **Hand rules**: `hand_total` (mod 10), `is_natural`, `player_should_draw`,
  and `banker_should_draw` implementing the full chemin de fer banque table.
- **`deal_outcome_probabilities`** enumerates every draw outcome (four to six
  cards), weighting each card by its value's share of the deck — the
  industry-standard infinite-deck computation — reproducing the canonical
  published player/banker/tie figures. A test cross-validates it against an
  independent brute-force re-enumeration, so the two implementations must agree
  or the suite fails.
- **`two_card_total_counts` / `hand_total_probabilities`** give the *exact*
  no-replacement two-card total distribution, and
  **`hand_collision_probability`** applies the birthday bound (via the
  elementary symmetric polynomial `n! * e_n`) to ask how likely it is that two
  of the seated Bonds are dealt the same total. That last step is the one
  **approximation** in the package: the per-hand marginal is exact, but the
  hands are then combined as independent, whereas a real deal draws them all
  from one shrinking shoe. `test_iid_approximation_is_not_exact` brute-forces a
  small deck where the gap is about four percentage points, so the caveat is
  demonstrated rather than merely asserted.

### 6. `escalation_ladder.py` — doctrine as an absorbing Markov chain

Kemeny–Snell analysis with exact numpy linear algebra over
`quiet → rumour → scandal → spectacle → catastrophe`. `_validate_transitions`
derives the absorbing set **from the matrix itself** — a row with a unit
diagonal and no outflow — never from a state's name, and rejects matrices with
no absorbing row or no transient row. `escalation_analysis` then computes the
fundamental matrix `N = (I - Q)^{-1}`, expected absorption times `t = N @ 1`,
the spectral radius of `Q` as the largest complex modulus of its eigenvalues,
and the absorption probability `B = N R` summed over every absorbing state.
`compare_doctrines` contrasts the spoof and sanctioned doctrines and reports
the acceleration factor.

## Support modules

- **`figures/plots.py`** — one `render_*_figure` per concept plus
  `render_all_figures`, driven by `FIGURE_FILENAMES`. Agg backend, fixed DPI,
  so re-running reproduces byte-identical PNGs. The manuscript references these
  through `FIGURE_*` tokens rather than literal filenames, so a rename here
  cannot silently break an image link.
- **`manuscript_variables.py`** — `generate_variables` recomputes every metric
  live from the domain core (identity and experiment parameters come from
  `manuscript/config.yaml`), `save_variables` writes sorted JSON, and
  `write_resolved_manuscript_tree` performs **strict** substitution into
  `output/manuscript/`: any unresolved token raises `ValueError` naming the
  section and the token. There is no draft mode — every token is computable.

## How `mission.py` implements the frozen `MissionProvider`

`mission.py` is the single adapter between the pure core and the FROZEN
`bond_api` protocol. **Its public shape must not change** — `bond-cli`, the
coordinator's reconcile, and the orchestrator consume it across all 33
packages.

### The discovery contract

| Symbol | Contract |
|---|---|
| `MissionProvider` | class at module top level; `film = "casino_royale_1967"` matches the package slug |
| `GADGETS` | module-level `dict[str, Any]` of JSON-safe gadget payloads |
| `GADGET_REGISTRY` | module-level `GadgetRegistry`, populated at import time so a coordinator that only calls `load_provider` still finds the gadgets |
| `register_gadgets(registry=None)` | hook that populates a caller-supplied registry (or a fresh one) and returns it |

Seven gadgets are registered: `roster`, `coordination`, `dispatch`,
`doctrine`, `identity`, `baccarat`, `escalation`.

### The five stages

Each stage is pure — the analyses run on canonical inputs with no RNG and no
wall clock, so `brief → recon → plan → execute → debrief` is byte-reproducible.

1. **`brief() -> MissionBrief`** — declares six objectives (one per concept),
   four `Asset`s (roster manifest, spoof doctrine, casino table, escalation
   ladder), and two `Constraint`s (determinism, frozen-protocol boundary).
2. **`recon(request: ReconRequest) -> ReconReport`** — runs all six analyses
   and returns **eight** `Finding`s in a fixed order: `goal` (echoing the
   request), then `overlap`, `conflict`, `dispatch`, `doctrine`, `identity`,
   `table`, `escalation`. The coordination model contributes two findings
   (`overlap` and `conflict`), so the count is not one per concept.
   `tests/test_mission.py` pins the exact tuple, so adding or dropping a
   finding fails the suite until this list is updated with it.
3. **`plan(brief: MissionBrief) -> MissionPlan`** — six `Step`s, one per
   concept module, whose `params` reference the assets declared in the brief.
4. **`execute(plan: MissionPlan) -> MissionOutcome`** — runs the six payload
   builders (`_coordination_payload`, `_dispatch_payload`, …), each returning
   JSON-safe dicts, and attaches `Provenance(package_version, seed=7,
   input_hash, wall_time_s=0.0)`. `_input_fingerprint()` is a sha256 over the
   canonical inputs, so an outcome can be audited without re-running anything.
5. **`debrief(outcome: MissionOutcome) -> Debrief`** — reads the outcome's
   results and formats the standing lessons.

### The adapter boundary rule

The domain modules communicate with `mission.py` through plain frozen
dataclasses and dicts; `mission.py` translates those into `bond_api` types, and
the core never sees them. Deepening the package means adding domain modules and
enriching the payloads *inside* these stages — never changing the stage
signatures, the class name, or the registry symbols.

## How to add a concept

1. Create the pure module in `src/casino_royale_1967/` — stdlib + numpy only,
   deterministic, fully typed and documented, no `bond_api` import.
2. Add a real-data test file `tests/test_<module>.py` covering the happy path,
   the edge cases, and every error branch.
3. Add the module name to `DOMAIN_MODULES` in `tests/test_layer_contract.py`
   (its completeness check fails until you do).
4. Wire the concept into `mission.py`: a plan step, a results payload, a gadget
   entry, and a recon finding — without altering the public shape above.
5. If it has a figure, add a `render_*_figure` plus a `FIGURE_FILENAMES` entry,
   and reference it from the manuscript through its `FIGURE_*` token.
6. Add tokens to `manuscript_variables.py` and reference them from a
   `manuscript/[0-9]*.md` section. Three gates enforce this: unused tokens
   fail, unknown tokens fail, and bare numerals in results prose fail.
7. Re-run the full gate (see [agent_instructions.md](agent_instructions.md)).

## Forbidden patterns

- No `infrastructure.*` import anywhere in `src/`.
- No `bond_api` import outside `mission.py`.
- No mock framework in `tests/`.
- No business logic inside `scripts/`.
- No hand-authored measured number in the manuscript.
