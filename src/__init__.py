"""Casino Royale (1967) — FIVE 00s mission software package.

PROJECT BOND film package for *Casino Royale* (1967), the five-Bond farce.
Implements six deterministic domain concepts plus a ``bond_api``-compatible
``MissionProvider`` adapter:

* :mod:`casino_royale_1967.coordination_farce` — multi-agent coordination-failure
  model (five agents, all codename *James Bond*): overlap and conflict detection,
  clearance violations, weighted coordination loss, and deterministic
  single-agent deduplication.
* :mod:`casino_royale_1967.dispatch_chaos` — tick-based agent dispatch simulation
  with duplicate agents and protocol violations (exclusive tasks, clearance,
  double-booking, duplicate orders, duplicate codenames).
* :mod:`casino_royale_1967.spoof_analyzer` — satirical ops-doctrine analyzer:
  lexical inversion scoring, rule-contradiction detection, oxymoron flags, and a
  normalized spoof index.
* :mod:`casino_royale_1967.identity_confusion` — information-theoretic identity
  model: a softmax routing confusion matrix, Shannon entropy / conditional
  entropy / mutual information / NMI, and Bayesian sighting resolution.
* :mod:`casino_royale_1967.baccarat_table` — chemin de fer hand and draw rules,
  exact enumerated deal odds, and the birthday-bound hand-collision probability
  across the Bonds seated at the table.
* :mod:`casino_royale_1967.escalation_ladder` — doctrine as an absorbing Markov
  chain: fundamental matrix, expected absorption times, spectral radius, and the
  spoof-versus-sanctioned acceleration factor.
* :mod:`casino_royale_1967.mission` — thin ``bond_api`` adapter exporting
  ``MissionProvider`` (slug ``casino_royale_1967``, codename *FIVE 00s*) and the
  film's gadget registry.

The six domain modules are pure and infrastructure-free (stdlib + numpy only).
They stay importable even when the ``bond-api`` path dependency is unavailable,
because ``casino_royale_1967.__init__`` resolves the adapter's exports lazily —
a property proven in a subprocess by ``tests/test_layer_contract.py``.
"""
