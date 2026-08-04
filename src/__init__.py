"""Casino Royale (1967) — FIVE 00s mission software package.

PROJECT BOND film package for *Casino Royale* (1967), the five-Bond farce.
Implements three deterministic domain concepts plus a ``bond_api``-compatible
``MissionProvider`` adapter:

* :mod:`casino_royale_1967.coordination_farce` — multi-agent coordination-failure
  model (five agents, all codename *James Bond*): overlap and conflict detection,
  weighted coordination loss, deterministic single-agent deduplication.
* :mod:`casino_royale_1967.dispatch_chaos` — tick-based agent dispatch simulation
  with duplicate agents and protocol violations (exclusive tasks, clearance,
  double-booking, duplicate orders, duplicate codenames).
* :mod:`casino_royale_1967.spoof_analyzer` — satirical ops-doctrine analyzer:
  lexical inversion scoring, rule-contradiction detection, oxymoron flags, and a
  normalized spoof index.
* :mod:`casino_royale_1967.mission` — thin ``bond_api`` adapter exporting
  ``MissionProvider`` (slug ``casino_royale_1967``, codename *FIVE 00s*) and the
  film's gadget registry.

The three domain modules are pure and infrastructure-free (stdlib + numpy only):
they stay importable even if the ``bond-api`` path dependency ever fails.
"""
