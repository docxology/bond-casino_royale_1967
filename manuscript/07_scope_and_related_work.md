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

The work sits at the intersection of three research threads:

- **Multi-agent coordination and conflict.** The overlap/conflict detection
  follows the classic line of research on coordination problems in
  multi-agent systems, where redundant or duplicative agents degrade system
  performance. The weighted-loss formulation is a small, reproducible
  instance of that family.
- **Deterministic simulation and protocol verification.** The dispatch
  simulator's rule-checker mirrors property-based protocol enforcement: each
  order is checked against a fixed rule set, and violations are recorded as
  first-class data — the same discipline used in lightweight runtime
  verification.
- **Reproducible computational research.** The project ships live-computed
  manuscript metrics, deterministic artifacts, and a frozen protocol adapter,
  following the template's reproducibility and zero-mock standards.

The *Casino Royale* (1967) material itself is in the public cultural
domain; this project uses its plot beats (baccarat championship, SMERSH
headquarters, the gamma-ray projector, Mata Bond) as a satirical dataset, not
as a claim about the film.
