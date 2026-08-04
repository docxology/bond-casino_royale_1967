# Abstract

*Casino Royale* (1967) is the spy farce in which five different operatives
answer to the same codename, James Bond. This project — codename **FIVE 00s** —
builds deterministic mission software around that premise. It implements and
tests three concepts drawn from the film's organizational failure:

1. **Coordination-farce model** (`coordination_farce.py`): a roster of
   {{CONFIG_NUM_AGENTS}} agents who all share the codename *James Bond*,
   assigned across {{CONFIG_NUM_TASKS}} tasks from the film's plot. The model
   detects **overlap** (multiple agents on one task) and **conflict**
   (agents on mutually exclusive task pairs), reports clearance violations,
   and computes a weighted coordination loss. The canonical assignment set of
   {{RESULT_ASSIGNMENTS}} orders yields
   {{RESULT_OVERLAP_COUNT}} overlaps and {{RESULT_CONFLICT_COUNT}} conflicts
   for a loss of **{{RESULT_COORDINATION_LOSS}}**.
2. **Dispatch-chaos simulation** (`dispatch_chaos.py`): a tick-based
   dispatch centre issues {{RESULT_ORDERS}} orders across the five Bonds and
   enforces five protocol rules (exclusive tasks, clearance, double-booking,
   duplicate orders, and duplicate codenames). {{RESULT_DISPATCHED}} orders
   dispatch successfully, {{RESULT_REJECTED}} are rejected as protocol
   violations, giving a chaos index of **{{RESULT_CHAOS_INDEX}}**.
3. **Spoof protocol analyzer** (`spoof_analyzer.py`): a lexical analyzer
   scores satirical ops doctrine against a sane protocol, detecting
   absolutist inversions and oxymorons. The film's standing orders score a
   spoof index of **{{RESULT_SPOOF_INDEX}} / 100**.

All three models are deterministic (fixed seed, no random draws, no wall
clock in artifacts) and are exposed as a `MissionProvider` implementing the
frozen `bond_api` protocol, with a gadget registry and publication-style
figures. Keywords: {{CONFIG_NUM_AGENTS}}-agent coordination failure, agent
dispatch simulation, protocol violations, satirical ops doctrine,
reproducible research.
