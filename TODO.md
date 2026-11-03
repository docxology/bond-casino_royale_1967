# TODO — casino_royale_1967 (FIVE 00s)

**FIVE 00s** is the PROJECT BOND film package for the 1967 *Casino Royale* — the
spy farce in which five operatives all answer to the codename *James Bond*. Six
pure domain modules model that coordination catastrophe (roster/overlap
analysis, a tick-based dispatch simulation, a lexical doctrine analyzer, an
information-theoretic identity model, chemin de fer deal odds and a
birthday-bound table-collision metric, and doctrine as an absorbing Markov
chain), exposed through the FROZEN `bond_api` `MissionProvider` protocol in the
single adapter `src/casino_royale_1967/mission.py`.

**Verified state today (measured this session, 2026-08-05):**
`uv run pytest tests/ --cov=src --cov-fail-under=90` → **245 passed, 100.00%
line+branch coverage on `src/`** (every one of the nine measured modules at
100.00%). `ruff check`, `ruff format --check` and `mypy src/ scripts/` all clean.
Regenerating twice through `scripts/z_generate_manuscript_variables.py` now
yields identical bytes (it did not before this session — see **Correctness**).
All eight findings in `output/verify/casino_royale_1967.json` were re-checked
against the tree at their recorded locations and are remediated — see
**Correctness** for exactly what was checked.

---

## Open work

### Correctness

**None open.** Every finding in the adversarial audit
(`../output/verify/casino_royale_1967.json`) was re-read against its recorded
location this session and is fixed in the current tree:

| Audit finding | Where it lived | Verified fixed by |
|---|---|---|
| SEVERE — false "single-deck play inverts the banker edge" | `manuscript/07_scope_and_related_work.md` | Line 44-46 now states the *opposite* — the claim is retracted, attributed, and scoped ("An earlier draft of this section asserted the opposite…") |
| Docs claim dedup "retires the overlap victims" when it did not | `coordination_farce.py`, `docs/architecture.md §1`, `02_methodology.md` | Both paths now derive from the shared `_winner_by_task` helper (`coordination_farce.py:224-225, 342-348`), and `tests/test_coordination_farce.py:218-229` asserts `report.overlap_victims == result.dropped_by_task` task-for-task |
| Wrong conditional-entropy direction, arithmetically self-contradictory | `03_results.md`, `04_conclusion.md` | `03_results.md:83-86` now names both directions and which one the manuscript reports; live tokens are arithmetically consistent (2.310 − 0.175 = 2.135 ambiguity; 2.322 − 0.175 = 2.147 residual) |
| Approximation stated as an exact probability | `03_results.md`, `02_methodology.md §5` | Named at `03_results.md:111-114` and `02_methodology.md:194-202`, with `test_iid_approximation_is_not_exact` as the demonstration |
| `STANDALONE.md` stale at Phase-2 (three modules) | `STANDALONE.md` | Now lists all six domain modules plus figures/variables/adapter, and carries the correct regenerate block |
| Bibliography never cited, therefore inert | `manuscript/references.bib` | All seven bib entries are cited across sections 01/02/03/07, and `tests/test_manuscript_variables.py:313-338` gates both directions (`test_every_bib_entry_is_cited`, `test_every_citation_resolves_to_a_bib_entry`) with a non-vacuity control |
| "one Finding per concept" vs 8 real findings | `README.md`, `docs/architecture.md` | `README.md:62` says "8 Findings (goal + 7 concept findings)"; `docs/architecture.md:191` explicitly says "the count is not one per concept". Live: `len(recon(...).findings) == 8` |
| Mislabeled dispatch metric row | `06_reproducibility.md` | Row 27 now reads "Single-agent deduplication of assignments (kept / dropped)", separated from the genuine dispatch rows on 28-29 |
| **SEVERE — false byte-for-byte regeneration claim** (found and fixed 2026-08-05, not part of the original audit) | `manuscript_variables.py:155,249`, asserted in `01_introduction.md:54-55`, `00_abstract.md:39`, `06_reproducibility.md:5-14`, `AGENTS.md:20` | `GENERATION_TIMESTAMP` was `datetime.now(UTC)` rendered into the manuscript and the token JSON, so two regenerations one second apart differed (`3732d6f5…` vs `be5a42fc…`). The wall clock is gone: `generate_variables` takes no `now=`, and the stamps are the committed `paper.date` / `paper.python_requires`. `tests/test_regeneration_determinism.py` regenerates twice through the production script and diffs every artifact; it was proven able to fail by reintroducing `datetime.now(UTC)` (3 of its 4 tests went red, naming the two drifted files) before restoring |

### Verification

Claims that are true today but are not bound by a test that can fail.

#### V1 — `data/claim_ledger.yaml` is inert: nothing reads it

- **What is wrong:** `data/claim_ledger.yaml` carries ten pinned claims
  (`coordination-loss: 15`, `dispatch-chaos-index: 0.615`, `spoof-index: 45.0`,
  `five-bonds-count: 5`, `task-count: 6`, `identity-nmi: 0.075`,
  `identity-resolution: bond_cooper`, `baccarat-player-odds: 0.4461`,
  `table-collision: 0.704`, `escalation-acceleration: 14.0`). A repo-wide grep
  finds exactly one reference to the file anywhere in the package —
  `README.md:125`, which merely says it exists. No test, script or gate loads
  it. I verified all ten values against `generate_variables(Path("."))` this
  session and they match, so the ledger is accurate *today* — but a constant
  change in `src/` would leave it silently stale with nothing failing.
- **Files:** `data/claim_ledger.yaml` (all 10 entries);
  `src/casino_royale_1967/manuscript_variables.py:generate_variables`.
- **Done looks like:** a new test (e.g. `tests/test_claim_ledger.py`) that loads
  the YAML and, for every claim whose `source_tier` is `generated_metric`,
  asserts the recorded `value` equals the live token from
  `generate_variables()`, plus a positive control that a deliberately wrong
  value fails the check.
- **Command:** `uv run pytest tests/test_claim_ledger.py -v`

#### V2 — Three audit corrections landed as prose with no guarding gate

- **What is wrong:** `../output/verify/casino_royale_1967.unresolved.json` entry
  3 records that findings 1, 5 and 8 were closed with
  `gate_proven_failable=false` — they are doc/prose corrections with nothing that
  breaks if they regress. Confirmed this session: `grep -rn "STANDALONE" tests/`
  returns nothing, and no test reads `manuscript/06_reproducibility.md` or the
  narrative sections of `README.md` / `docs/architecture.md`. A future edit can
  silently reintroduce any of the three.
- **Files:** `STANDALONE.md` (Purpose module table, lines 15-25);
  `manuscript/06_reproducibility.md:27-29` (the dedup vs dispatch rows);
  `manuscript/07_scope_and_related_work.md:41-46` (the retracted single-deck
  claim).
- **Done looks like:** each corrected claim is bound to code. Concretely: a test
  that asserts `STANDALONE.md`'s module table names every module in
  `test_layer_contract.DOMAIN_MODULES` (so adding a seventh module fails the
  doc), and a test asserting the `06_reproducibility.md` snapshot table's dedup
  row label does not contain the word "Dispatch". Each with a positive control.
- **Command:** `uv run pytest tests/ -k "standalone or reproducibility" -v`

#### V3 — `mean_delay` is structurally `0.0` and no test says so

- **What is wrong:** `dispatch_chaos.py:250` hardcodes `mean_delay = 0.0` (the
  reject model never requeues), it is carried on `DispatchReport`
  (`dispatch_chaos.py:98`) and published in the mission results
  (`mission.py:165`) — but `grep -n "mean_delay" tests/*.py` returns **nothing**.
  100% coverage does not help here: the line executes, its value is never
  asserted. A future change that makes it non-zero would break no test.
- **Files:** `src/casino_royale_1967/dispatch_chaos.py:98, 250, 258`;
  `src/casino_royale_1967/mission.py:165`.
- **Done looks like:** `tests/test_dispatch_chaos.py` asserts
  `simulate_dispatch(CHAOS_ORDERS).mean_delay == 0.0` with a docstring naming the
  reject-model premise, so the invariant is pinned until V-E2 replaces it.
- **Command:**
  `uv run pytest tests/test_dispatch_chaos.py -k mean_delay -v`

#### V4 — Identity model's free parameters are unmeasured

- **What is wrong:** `CONFUSION_TEMPERATURE = 1.0`
  (`identity_confusion.py:67`) and the four likelihood constants
  (`identity_confusion.py:81-84`: `LIKELIHOOD_JURISDICTION_MATCH = 0.9`,
  `LIKELIHOOD_JURISDICTION_MISS = 0.2`, `LIKELIHOOD_CLEARANCE_OK = 0.95`,
  `LIKELIHOOD_CLEARANCE_SHORT = 0.4`) are documented, deterministic choices. The
  only tests touching them are range checks
  (`tests/test_identity_confusion.py:168-169`, `0 < x < 1`). Nothing measures how
  much the headline `RESULT_IDENTITY_NMI = 0.075` or the Bayesian resolution
  (`bond_cooper`, confidence `0.613`) depends on them, so the manuscript's
  "routing carries almost no information" claim could be an artefact of one
  parameter setting.
- **Files:** `src/casino_royale_1967/identity_confusion.py:67, 81-84`;
  claim surfaces `manuscript/03_results.md:70-86`,
  `manuscript/04_conclusion.md:23-24`.
- **Done looks like:** a sweep over temperature and the likelihood table with
  the NMI range reported as a manuscript token (e.g. `RESULT_IDENTITY_NMI_RANGE`),
  and a test pinning that the NMI stays below some stated ceiling across the
  swept grid. Until then the manuscript must not imply parameter-independence.
- **Command:**
  `uv run pytest tests/test_identity_confusion.py -k sensitivity -v && uv run python scripts/z_generate_manuscript_variables.py`

#### V5 — The corrected baccarat claim rests on a source this sandbox cannot fetch

- **What is wrong:** `../output/verify/casino_royale_1967.unresolved.json` entry
  2 records that the remediation of the SEVERE finding could not independently
  re-fetch Wizard of Odds (`wizardofodds.com` is outside the sandbox's network
  allowlist). The correction was therefore kept qualitative and attributed. The
  quantitative half — the actual single-deck banker/player figures — is cited
  but never re-verified in this repo.
- **Files:** `manuscript/07_scope_and_related_work.md:41-46`;
  `manuscript/references.bib` (`@misc{wizardofodds_baccarat}`).
- **Done looks like:** either (a) the source is fetched from a network-enabled
  session and the figures recorded verbatim next to the citation with an access
  date, or (b) the sentence is rewritten to depend only on
  `deal_outcome_probabilities`' own infinite-deck scope (which the code *can*
  prove) and the external citation demoted to further reading.
- **Command:** `uv run pytest tests/test_baccarat_table.py -v` plus a manual
  re-read of `manuscript/07_scope_and_related_work.md:41-46`.

#### V6 — The pinned `ruff` gate is red, and the recorded caveat reproduces exactly

- **What is wrong:** the two `ruff` rows of "## Verification" below do not hold
  for this tree. Measured 2026-11-03 against the `origin/main` bytes of
  `8aa4e7d`, with the pinned `ruff 0.16.1` taken from this repository's own
  venv:

  | Command | Result |
  |---|---|
  | `ruff check src/ scripts/ tests/` | `Found 28 errors` — RUF100 ×11, RUF022 ×8, PLW1510 ×2, I001 ×2, EXE001 ×2, TRY004, B033, B023; 21 fixable |
  | `ruff check src/ scripts/` (`AGENTS.md` scope) | `Found 22 errors` — RUF100 ×9, RUF022 ×8, EXE001 ×2, TRY004, I001, B023 |
  | `ruff format --check src/ scripts/ tests/` | `21 files would be reformatted, 9 files already formatted` |
  | `ruff format --check src/ scripts/` | `10 files would be reformatted, 6 files already formatted` |
  | `mypy src/ scripts/` | clean, 14 files (mypy 2.3.0) |

  This is neither new debt nor drift: the **Caveat (checked 2026-10-25)** in the
  same section named *28 hits* on the same eight rules and *21 files* for
  `ruff format` over the same scope, and both reproduce exactly here. The
  `pytest` and `mypy` rows do hold; what stays open is the lint half of the
  caveat, which the suite cannot see. No `[tool.ruff]` section ships, so only
  tool defaults apply, and the two scopes above differ only by `tests/`.
- **Files:** 28 findings across `src/`, `scripts/` and `tests/`;
  `ruff check --output-format=concise` prints `file:line:code` for every one.
  Both `EXE001` findings are mode-only (`scripts/*.py`), the two `PLW1510` and
  the `B033` are in `tests/`.
- **Done looks like:** either a `[tool.ruff]` section that states the intended
  rule set and line length, after which the tree is brought to it (one rule per
  commit, behaviour-changing suppressions carrying their reason), or an
  explicit decision to accept the reformat on the record. The gate is the
  pinned `ruff` from `uv.lock`, not whichever `ruff` is first on `PATH`.
- **Command:** `uv run --extra dev ruff check src/ scripts/ tests/ && uv run --extra dev ruff format --check src/ scripts/ tests/`

### Documentation

#### D1 — "33 BOND packages" does not match the tree

- **What is wrong:** three docs assert the frozen protocol is consumed "across
  all 33 BOND packages". Measured this session, the suite root
  (`projects/working/bond/`) holds **27 film packages + 7 shared packages = 34**
  (excluding `_omnibus/`, `_prompts/`, `output/`, `tests/`, `__pycache__/`), and
  `bond-coordinator/src/bond_coordinator/registry.py:390` describes a "27-film
  roster". The number 33 matches no denominator I can find.
- **Files:** `AGENTS.md:66`; `docs/agent_instructions.md:62`; `docs/AGENTS.md:23`.
- **Done looks like:** all three sites carry one number with a named denominator
  (e.g. "all 27 film packages" or "all 34 BOND packages"), consistent with the
  coordinator roster.
- **Command:**
  `grep -rn "33" AGENTS.md docs/*.md` returns no package-count claim, and
  `ls -d ../*/ | wc -l` corroborates whatever number replaces it.

### Extension

#### E1 — Delegate provenance persistence to `bond_utilities.mission_io`

- **Status: UNBLOCKED as of this session.** The blocker recorded in the previous
  TODO ("bond-utilities shipping `mission_io`") is resolved:
  `bond-utilities/src/bond_utilities/mission_io.py:153` ships
  `record_provenance_outcome`, and two sibling films already use it
  (`goldeneye/scripts/execute.py:42`, `the_world_is_not_enough/scripts/execute.py:36`).
- **What is missing here:** `scripts/mission.py:run_execute` (lines 59-72) hand-
  serialises the outcome to *stdout only* — it writes no artifact at all, and
  `pyproject.toml` does not declare `bond-utilities` as a dependency (only
  `bond-api`, line 23 / `[tool.uv.sources]` line 37).
- **Determinism constraint (read before implementing):**
  `record_provenance_outcome` defaults `started_at` to
  `datetime.now(timezone.utc)`. The goldeneye call site does not override it, so
  its record is *not* byte-reproducible. This package claims byte-reproducibility
  (`README.md:73-74`) and now *enforces* it
  (`tests/test_regeneration_determinism.py`), so any binding here must pass an
  explicit `started_at=` derived from committed inputs — `paper.date` in
  `manuscript/config.yaml` is the established source — and never the wall clock.
  If that proves impossible, the outcome artifact must be excluded from the
  covered set in `test_regeneration_determinism._COVERED` *and* the claim
  narrowed in words; do not soften the wording while leaving the claim broad.
- **Done looks like:** `scripts/mission.py execute` writes
  `output/data/five00s_mission.json` through `record_provenance_outcome` with a
  fixed `started_at`; the file's `provenance.input_hash` equals
  `outcome.provenance.input_hash`; and a test runs the CLI twice and asserts the
  two files are byte-identical.
- **Command:**
  `uv run python scripts/mission.py execute && uv run pytest tests/test_scripts_smoke.py -k provenance -v`

#### E2 — A queueing variant of the dispatch model

- **What is missing:** `simulate_dispatch` is a reject model — a rejected order
  is dropped and never requeued, which is why `mean_delay` is always `0.0` (see
  V3). That is a deliberate premise (chaotic dispatch loses orders), documented
  at `docs/architecture.md:76-78`, but it leaves a report field that carries no
  information.
- **Files:** `src/casino_royale_1967/dispatch_chaos.py:181-260`;
  `docs/architecture.md:76-78`.
- **Done looks like:** either a `simulate_dispatch(..., requeue=True)` variant
  producing a non-trivial delay distribution with its own real-data tests, or
  removal of `mean_delay` from `DispatchReport` and `mission.py:165`. Do not
  leave a field that is structurally always zero.
- **Command:** `uv run pytest tests/test_dispatch_chaos.py -v`

#### E3 — Quantify the without-replacement collision error

- **What is missing:** the exact without-replacement value of the five-Bond
  hand-collision probability for a 52-card shoe is **not computed** — this is the
  single item in `../output/verify/casino_royale_1967.unresolved.json` entry 1.
  The i.i.d.-across-hands approximation is now named everywhere the `0.704`
  figure appears and is proven inexact on a small deck
  (`test_iid_approximation_is_not_exact`), but the error magnitude for the real
  shoe is unquantified. An exact enumeration of ten cards from fifty-two was
  judged too slow for the suite.
- **Files:** `src/casino_royale_1967/baccarat_table.py`
  (`distinct_total_probability`, `hand_collision_probability`);
  claim surfaces `manuscript/03_results.md:106-114`,
  `manuscript/02_methodology.md:194-202`, `STANDALONE.md:67-69`.
- **Done looks like:** a bound or a Monte-Carlo estimate of the gap (with its own
  seed and confidence interval), reported as a manuscript token, so readers can
  see how far `0.704` is from the exact figure. Until then the accepted
  limitation below stands.
- **Command:** `uv run pytest tests/test_baccarat_table.py -k collision -v`

---

## Known limitations (not bugs)

Recorded so nobody re-litigates them. None of these is a TODO item.

- **The hand-collision figure `0.704` is approximate, and its error is
  unquantified.** Within a hand the two-card distribution is exact and without
  replacement; *across* the five seated Bonds the birthday bound treats hands as
  i.i.d. The assumption is stated in the `distinct_total_probability` and
  `hand_collision_probability` docstrings, in `02_methodology.md:194-202`, in
  `03_results.md:111-114` and in `STANDALONE.md:67-69`, and
  `test_iid_approximation_is_not_exact` shows on a small deck that the gap is
  real (about four percentage points there). **Honest scope: anyone quoting
  `0.704` must quote it as approximate.** Quantifying the gap is E3.

- **`deal_outcome_probabilities` is an infinite-deck (with-replacement)
  computation and says nothing about finite-deck play in either direction.**
  This is the softened form of the SEVERE audit finding: the manuscript
  previously asserted that single-deck play inverts the banker edge; that claim
  is retracted at `manuscript/07_scope_and_related_work.md:44-46` and the
  package's own claim is now scoped to the model it actually computes.
  `STANDALONE.md:70-71` says the same. Re-verifying the external finite-deck
  figures is V5; the *scoping* itself is settled.

- **`deduplicate_assignments` leaves one irreducible conflict.** It removes every
  overlap, but a single agent must still win the baccarat championship while
  another burns the same table, so one conflict persists by design. Documented in
  `manuscript/02_methodology.md`; not a defect.

- **`mean_delay` is `0.0` by premise, not by accident.** The reject model loses
  orders rather than queueing them. Accepted until E2 decides between a queueing
  variant and removing the field. V3 only asks that the current value be pinned.

- **The spoof index and chaos index are satirical diagnostics.** Lexical measures
  over declared marker tables, not validated instruments for real organisational
  doctrine. Stated in `manuscript/07_scope_and_related_work.md` and
  `STANDALONE.md:64-66`.

- **No token is environment-dependent — fixed 2026-08-05.** This entry
  previously read "`GENERATION_TIMESTAMP` and `PYTHON_VERSION` are the only
  environment-dependent tokens … Not a determinism violation." That was wrong,
  and it was the load-bearing wrong claim: `GENERATION_TIMESTAMP` was
  `datetime.now(UTC)` rendered into `06_reproducibility.md` and into
  `output/data/manuscript_variables.json`, so the package's byte-for-byte
  regeneration claim was false on every run. `test_deterministic_with_fixed_now`
  did not pin the behaviour — it passed the same `now=` to both calls, fixing
  the only value that varied, which is why the breach survived a green suite.
  Both tokens are now derived from committed config (`paper.date` →
  `MANUSCRIPT_DATE`, `paper.python_requires` → `PYTHON_REQUIRES`),
  `generate_variables` has no `now=` parameter at all, and
  `tests/test_regeneration_determinism.py` regenerates the tree twice through
  the production script and diffs the bytes.

- **No DOI.** The tree is pushed to
  `github.com/docxology/bond-casino_royale_1967` but is not registered with
  Zenodo, so no DOI belongs in the sidecars (see `STANDALONE.md`).

- **The `bond_api` surface is FROZEN.** `MissionProvider`, the five stage
  methods, `GADGETS`, `GADGET_REGISTRY` and `register_gadgets` cannot change
  signature — `bond-cli`, the coordinator's reconcile and the orchestrator's
  `FilmProviderAdapter` consume them fleet-wide. Deepen inside the stages;
  never change a signature. Discovery is already proven end-to-end here
  (`tests/test_mission.py:246-258` loads this film via
  `bond_api.discovery.load_provider` and `discover`, and
  `test_mission_registry_registers_provider_by_slug` registers it into the real
  `bond_api.registry.MissionRegistry`) — the previous TODO's "blocked on
  bond-coordinator shipping MissionRegistry" item is **done and removed**.

---

## Verification

The gate for this package, run from the repository root:

```bash
uv sync --all-extras
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
grep -rn "unittest.mock\|MagicMock\|@patch\|create_autospec" tests/ || echo Clean
git status --short
```

**Expected outcomes (all observed this session, 2026-08-05):**

| Command | Expected |
|---|---|
| `pytest … --cov-fail-under=90` | every test passes, `TOTAL … 100.00%`, "Required test coverage of 90% reached" |
| `ruff check` | `All checks passed!` |
| `ruff format --check` | `26 files already formatted` |
| `mypy src/ scripts/` | `Success: no issues found in 14 source files` |
| mock grep | no matches (prints `Clean`) |
| `git status --short` | empty after commit |

**Caveat (checked 2026-10-25):** the `ruff`/`mypy` rows above do not reproduce
with the versions this repo pins — `uv.lock` holds ruff 0.16.1 and mypy 2.3.0.
The pinned ruff, run isolated or not, reports 28 hits over the same sources —
`RUF022`, `I001`, `RUF100`, `EXE001`, `B023`, `B033`, `TRY004`, `PLW1510` — and
21 files `ruff format` would restyle; ruff 0.17.2 agrees, and mypy 2.4.0
reports one `unused-ignore` at `identity_confusion.py:158`. No `[tool.ruff]`
section ships in this repository, so only tool defaults apply: re-establish one
(or accept a reformat) before trusting an "all clean" claim. The mock grep, the
layer-contract import gate and the 90% coverage floor are unaffected.

Artifact regeneration (writes only under the git-ignored `output/`):

```bash
uv run python scripts/mission.py execute    # deterministic outcome JSON on stdout
uv run python scripts/mission.py figures    # six deterministic PNGs
uv run python scripts/z_generate_manuscript_variables.py  # tokens + figures + resolved tree
```

Re-running these must leave `git status --short` empty.

> **Sandbox note:** if any `uv` command fails with `Failed to initialize cache at
> /Users/4d/.cache/uv`, that is a sandbox restriction on `uv`'s cache directory,
> not a package failure. Re-run the identical command outside the sandbox.
