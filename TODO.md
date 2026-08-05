# TODO — Casino Royale (1967) · FIVE 00s

Build & maintenance state for this PROJECT BOND film package.

## Done (phase 4 — deep improvement)

- [x] `src/casino_royale_1967/identity_confusion.py` — information-theoretic
      identity model: feature-vector softmax confusion matrix, Shannon
      entropy / conditional entropy / mutual information / NMI, and Bayesian
      sighting resolution. Canonical: routing NMI 0.075, identity ambiguity
      2.13 bits, sighting resolves to `bond_cooper` (confidence 0.613).
- [x] `src/casino_royale_1967/baccarat_table.py` — exact baccarat
      (chemin de fer) table: hand/draw rules, infinite-deck deal odds that
      reproduce the canonical published figures (player 0.4461, banker
      0.4584, tie 0.0954; Wizard of Odds / Ethier), and the five-Bond
      hand-collision birthday metric (0.704).
- [x] `src/casino_royale_1967/escalation_ladder.py` — doctrine as an
      absorbing Markov chain: fundamental matrix `(I-Q)^{-1}`, expected
      absorption times, spectral radius; the spoof doctrine reaches
      catastrophe in 4.0 steps vs 56.0 under discipline (14.0x faster).
- [x] Mission deepened inside (public shape unchanged): six objectives, four
      assets, six plan steps, six results payloads, seven gadgets
      (+ `identity`, `baccarat`, `escalation`); still a FROZEN
      `MissionProvider` for bond-cli / coordinator / orchestrator.
- [x] Manuscript variables: new `RESULT_IDENTITY_*`, `RESULT_BACCARAT_*`,
      `RESULT_TABLE_*`, `RESULT_ESCALATION_*` and `CONFIG_TABLE_BONDS` tokens.
- [x] Three new figures: `identity_confusion.png`, `baccarat_odds.png`,
      `escalation_ladder.png` (six total).
- [x] Tests: `test_identity_confusion.py`, `test_baccarat_table.py`,
      `test_escalation_ladder.py` plus mission/vars/figures/scripts updates;
      baccarat is cross-validated against an independent brute-force
      reference. 182 tests, ~99.8% coverage on `src/`.
- [x] Manuscript: methodology (sections 4-6), results (identity / table /
      escalation), conclusion, abstract, setup, reproducibility, scope, and
      `references.bib` (Shannon 1948, Kemeny-Snell 1960, Ethier 2010,
      Wizard of Odds) updated.

## Done (phase 2)

- [x] `src/casino_royale_1967/coordination_farce.py` — five-Bond
      coordination-failure model: overlap/conflict/clearance detection,
      weighted loss, single-agent deduplication. Real data (the five cast
      members), deterministic.
- [x] `src/casino_royale_1967/dispatch_chaos.py` — tick-based dispatch
      simulation enforcing five protocol rules; deterministic chaos index and
      success ratio; all five rule classes exercised by the canonical scenario.
- [x] `src/casino_royale_1967/spoof_analyzer.py` — satirical ops-doctrine
      analyzer: word-boundary marker scoring, rule-contradiction detection,
      oxymoron flags, normalised spoof index (45.0 / 100 for the film doctrine).
- [x] `src/casino_royale_1967/mission.py` — `MissionProvider` implementing the
      FROZEN `bond_api` protocol (slug `casino_royale_1967`, codename
      `FIVE 00s`); gadget registry (`roster`, `coordination`, `dispatch`,
      `doctrine`); deterministic provenance (seed 7, sha256 input fingerprint,
      `wall_time_s=0.0`).
- [x] `src/casino_royale_1967/manuscript_variables.py` — live `{{TOKEN}}`
      hydration from `manuscript/config.yaml` + the domain core; strict
      resolved-manuscript tree writer.
- [x] `src/casino_royale_1967/figures/plots.py` — three deterministic PNGs
      (coordination load, dispatch timeline, spoof scores).
- [x] `scripts/mission.py` — thin brief/recon/plan/execute/debrief/figures CLIs.
- [x] `scripts/z_generate_manuscript_variables.py` — token map + figures +
      resolved-manuscript injection.
- [x] Tests: `test_coordination_farce.py`, `test_dispatch_chaos.py`,
      `test_spoof_analyzer.py`, `test_mission.py` (protocol/registry/
      serialization/discovery), `test_manuscript_variables.py` (live
      cross-reference), `test_scripts_smoke.py`, `test_figures.py`. Zero mocks.
- [x] Manuscript (`manuscript/`) with live tokens + 3 figures; docs, README,
      AGENTS, metadata sidecars rewritten for the FIVE 00s identity.
- [x] Gates green: pytest `--cov=src --cov-fail-under=90` (99%+), ruff
      check+format, mypy, zero lineage strings, git status clean.

## Declared integration points

- **bond-api (FROZEN, bound):** `pyproject.toml` declares a local path
  dependency via `[tool.uv.sources] bond-api = { path = "..." }`. `mission.py`
  is the only module importing `bond_api`; the pure domain core stays
  importable if the path dep ever fails. Bound and verified in this phase.
- **bond-utilities `mission_io.record_provenance_outcome` (not yet bound):**
  the mission currently carries `Provenance` inline. Once
  `bond_utilities.mission_io` is a converted dependency, delegate persistence
  to `record_provenance_outcome` so the outcome record schema matches the
  shared fleet contract. Acceptance: outcome JSON written through the shared
  helper with the same `input_hash` and deterministic JSON.
- **bond-coordinator / orchestrator discovery:** provider is discoverable by
  slug (`load_provider('casino_royale_1967')`) and gadgets are on the module
  registry; bind into fleet `MissionRegistry` when the coordinator ships.

## Notes / known trade-offs

- `dispatch_chaos` is a reject-model: a rejected order is dropped, never
  requeued, so `mean_delay` is always 0. Documented as the chaotic-dispatch
  premise; a queueing variant is future work.
- `deduplicate_assignments` removes every overlap but leaves the single
  irreducible baccarat-win-vs-burn clash (one conflict, loss equal to the
  conflict weight) — by design, documented in the manuscript.
