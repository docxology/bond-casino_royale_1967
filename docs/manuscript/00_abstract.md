# Abstract

*Casino Royale* (1967) is the spy farce in which five different operatives
answer to the same codename, James Bond. This project — codename **FIVE 00s** —
builds deterministic mission software around that premise. It implements and
tests six concepts drawn from the film's organizational failure:

1. **Coordination-farce model** (`coordination_farce.py`): a roster of
   {{CONFIG_NUM_AGENTS}} agents who all share the codename *James Bond*,
   assigned across {{CONFIG_NUM_TASKS}} tasks. It detects **overlap**,
   **conflict**, and clearance violations, and computes a weighted
   coordination loss of **{{RESULT_COORDINATION_LOSS}}** from
   {{RESULT_OVERLAP_COUNT}} overlaps and {{RESULT_CONFLICT_COUNT}} conflicts.
2. **Dispatch-chaos simulation** (`dispatch_chaos.py`): a tick-based dispatch
   centre issues {{RESULT_ORDERS}} orders and enforces
   {{CONFIG_PROTOCOL_RULES}} protocol rules;
   {{RESULT_DISPATCHED}} dispatch successfully, {{RESULT_REJECTED}} are
   rejected, for a chaos index of **{{RESULT_CHAOS_INDEX}}**.
3. **Spoof protocol analyzer** (`spoof_analyzer.py`): lexical scoring of
   satirical ops doctrine against a sane protocol; the film's standing orders
   score **{{RESULT_SPOOF_INDEX}} / 100**.
4. **Identity-confusion model** (`identity_confusion.py`): information theory
   over the shared codename — routing carries only
   {{RESULT_IDENTITY_NMI}} normalized mutual information, leaving a dispatch
   ambiguity `H(routed | intended)` of {{RESULT_IDENTITY_AMBIGUITY}} bits, and
   a Bayesian sighting resolves to *{{RESULT_IDENTITY_RESOLUTION}}* with
   confidence {{RESULT_IDENTITY_CONFIDENCE}}.
5. **Baccarat table model** (`baccarat_table.py`): combinatorial deal odds
   exact for the infinite-deck model (player {{RESULT_BACCARAT_PLAYER}}, banker
   {{RESULT_BACCARAT_BANKER}}, tie {{RESULT_BACCARAT_TIE}}) and a
   {{CONFIG_TABLE_BONDS}}-Bond table collision probability of
   {{RESULT_TABLE_COLLISION}} under an i.i.d.-across-hands approximation.
6. **Escalation-ladder model** (`escalation_ladder.py`): the doctrine as an
   absorbing Markov chain — the spoof doctrine reaches catastrophe in
   {{RESULT_ESCALATION_SPOOF}} steps versus
   {{RESULT_ESCALATION_SANCTIONED}} under discipline, a
   {{RESULT_ESCALATION_ACCELERATION}}× acceleration.

All six models are deterministic (fixed seed, no random draws, no wall clock
in artifacts) and are exposed through a `MissionProvider` implementing the
frozen `bond_api` protocol, with a gadget registry and publication-style
figures. Keywords: {{CONFIG_NUM_AGENTS}}-agent coordination failure, agent
dispatch simulation, protocol violations, satirical ops doctrine, identity
confusion, baccarat odds, absorbing Markov chains, reproducible research.
