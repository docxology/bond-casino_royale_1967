# TODO — Casino Royale (1967) · FIVE 00s

Remaining work for this PROJECT BOND film package. Completed build history is
not tracked here — read the git log for that. This file is only what is *not*
done.

## Open work

### 1. Bind `bond_utilities.mission_io.record_provenance_outcome`

`mission.py` currently carries `Provenance` inline and `scripts/mission.py`
serialises the outcome itself. Once `bond_utilities.mission_io` is a converted
dependency, delegate persistence to `record_provenance_outcome` so this
package's outcome record matches the shared fleet schema.

- **Blocked on:** `bond-utilities` shipping `mission_io`.
- **Acceptance:** outcome JSON written through the shared helper, with the same
  `input_hash` and byte-identical deterministic JSON as today. A regression
  test must compare the helper's output against the current serialisation.

### 2. Register with the fleet `MissionRegistry`

The provider is discoverable by slug (`load_provider('casino_royale_1967')`)
and the gadgets sit on the module-level registry, but nothing binds this
package into a fleet-wide registry yet.

- **Blocked on:** `bond-coordinator` shipping `MissionRegistry`.
- **Acceptance:** the coordinator's reconcile lists this film with its seven
  gadgets, and an orchestrator DAG can run its five stages without importing
  anything from `src/` directly.

### 3. A queueing variant of the dispatch model

`dispatch_chaos.simulate_dispatch` is a **reject model**: a rejected order is
dropped and never requeued, which is why `DispatchReport.mean_delay` is always
`0.0`. That is a deliberate premise (chaotic dispatch loses orders), not a bug
— but it means the `mean_delay` field carries no information today.

- **Acceptance:** either a `simulate_dispatch(..., requeue=True)` variant that
  produces a non-trivial delay distribution with its own tests, or removal of
  `mean_delay` from the report if the reject model is declared final. Do not
  leave a field that is structurally always zero.

### 4. Sensitivity of the identity model to its free parameters

`CONFUSION_TEMPERATURE` and the four `LIKELIHOOD_*` constants are documented,
deterministic choices, but nothing measures how much the headline NMI and the
Bayesian resolution depend on them.

- **Acceptance:** a sweep over temperature and the likelihood table reported as
  manuscript tokens, so the claim "routing carries almost no information" is
  shown to be robust rather than an artefact of one parameter setting. Until
  then the manuscript should not imply parameter-independence.

## Known trade-offs (accepted, not work items)

- **`deduplicate_assignments` leaves one irreducible conflict.** It removes
  every overlap, but a single agent must still win the baccarat championship
  while another burns the same table, so one conflict persists by design. This
  is documented in the methodology, not a defect.
- **The birthday metric assumes independence across hands.** Within a hand the
  two-card distribution is exact and without replacement; *across* the seated
  Bonds the collision bound treats hands as i.i.d. This approximation is stated
  in the `distinct_total_probability` docstring and in the methodology.
- **The spoof index is a satirical diagnostic.** It is a lexical measure over
  declared marker tables, not a validated instrument for real organisational
  doctrine. `07_scope_and_related_work.md` says so explicitly.

## Integration points (stable, no action needed)

- **bond-api (FROZEN, bound).** `pyproject.toml` declares the local path
  dependency; `mission.py` is the only module importing `bond_api`, and
  `tests/test_layer_contract.py` proves the domain core imports without it.
- **Discovery contract.** `MissionProvider`, the five stage methods, `GADGETS`,
  `GADGET_REGISTRY` and `register_gadgets` are frozen. Any change here breaks
  `bond-cli`, the coordinator and the orchestrator across all 33 packages.
