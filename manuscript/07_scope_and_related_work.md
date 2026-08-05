# Scope and Related Work

## Scope

**FIVE 00s** models the coordination failure motif of *Casino Royale* (1967)
at the level of deterministic, hand-built algorithms. It does not attempt:

- a general agent-based simulation framework (the tick model is purpose-built
  for the farce, not a full discrete-event engine);
- machine-learned or stochastic dispatch policies (dispatch is a pure
  function of the deterministic order stream);
- a normative claim about real organizational governance — the "chaos index"
  is a satirical diagnostic, not a validated operations metric.

The satirical doctrine in `CANONICAL_SPOOF_DOCTRINE` is analyzed as *text*:
the analyzer measures lexical inversion and rule contradiction, and makes no
claim about the film's production history or intent.

## Related work

The work sits at the intersection of several research threads:

- **Multi-agent coordination and conflict.** The overlap/conflict detection
  follows the classic line of research on coordination failure in multi-agent
  systems, where redundant or duplicative agents degrade system performance.
  The weighted-loss formulation is a small, reproducible instance of that
  family.
- **Information theory of identity.** The identity-confusion model applies
  Shannon's entropy and mutual information to quantify how much identity a
  shared codename destroys; the Bayesian resolution is a standard posterior
  update over the roster (Shannon 1948; Cover & Thomas 2006). The
  normalization of mutual information by the larger marginal entropy follows
  the convention of Strehl & Ghosh (2002).
- **Deterministic simulation and protocol verification.** The dispatch
  simulator's rule-checker mirrors property-based protocol enforcement: each
  order is checked against a fixed rule set, and violations are recorded as
  first-class data.
- **Gambling mathematics.** The baccarat table's deal odds reproduce the
  canonical published figures of the chemin de fer drawing rules; the
  hand-collision metric is a birthday-bound application over the exact
  two-card-total distribution [@ethier2010doctrine; @wizardofodds_baccarat].
  Deck count shifts these probabilities only slightly and does **not** reverse
  their order: the banker bet is still the better side at one deck in the
  published tables [@wizardofodds_baccarat]. An earlier draft of this section
  asserted the opposite — that single-deck play inverts the banker edge — which
  its own cited source contradicts. This model cannot settle the question
  either way: `deal_outcome_probabilities` weights each card by its value's
  share of the shoe *with replacement*, so it is an infinite-deck computation
  and carries no finite-deck depletion effect at all.
- **Absorbing Markov chains.** The escalation ladder's fundamental matrix and
  expected absorption times follow Kemeny and Snell's classical treatment.
- **Reproducible computational research.** The project ships live-computed
  manuscript metrics, deterministic artifacts, and a frozen protocol adapter.

The *Casino Royale* (1967) material itself is in the public cultural
domain; this project uses its plot beats (baccarat championship, SMERSH
headquarters, the gamma-ray projector, Mata Bond, the five-Bond premise) as a
satirical dataset, not as a claim about the film.
