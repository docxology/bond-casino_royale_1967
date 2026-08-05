"""Identity confusion model — the five-Bond codename collapse.

In *Casino Royale* (1967) five physical operatives answer to the *same*
codename, James Bond. This module quantifies the resulting identity failure
with real information theory and Bayesian inference:

* a **confusion matrix** over the five physical agents — the probability that
  an order intended for agent *i* is routed to agent *j*, built
  deterministically as a softmax over agent-feature similarity (normalized
  clearance + a one-hot over the roster's distinct jurisdictions, *not* over
  the task catalog);
* **information-theoretic metrics**: prior entropy of the intended identity,
  conditional entropy of routing given intent (``H(routed | intended)`` — the
  expected confusion per dispatch), the reverse conditional entropy
  ``H(intended | routed) = H(intended) - I`` (what is still unknown about the
  intended Bond after seeing where the order landed), marginal routing
  entropy, mutual information, and normalized mutual information — plus the
  satirical headline that the *codename* itself carries zero bits (all five
  share it). The two conditional entropies are different numbers and are kept
  distinct throughout: ``H(routed | intended)`` subtracts from ``H(routed)``,
  ``H(intended | routed)`` subtracts from ``H(intended)``;
* **Bayesian identity resolution**: given a sighting's evidence (jurisdiction
  match, clearance sufficiency) the model computes the posterior over the
  five physical agents and reports the argmax resolution with its confidence.

Pure domain logic: stdlib + numpy only, no ``infrastructure`` / ``bond_api``
imports. Deterministic: the confusion matrix is a pure function of the
declared roster/tasks and the temperature; no RNG, no wall clock.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from casino_royale_1967.coordination_farce import (
    AGENT_ROSTER,
    TASK_CATALOG,
    Agent,
    Task,
)

__all__ = [
    "CONFUSION_TEMPERATURE",
    "IdentityReport",
    "IdentityResolution",
    "LIKELIHOOD_CLEARANCE_OK",
    "LIKELIHOOD_CLEARANCE_SHORT",
    "LIKELIHOOD_JURISDICTION_MISS",
    "LIKELIHOOD_JURISDICTION_MATCH",
    "TASK_JURISDICTIONS",
    "analyze_identity",
    "build_confusion_matrix",
    "conditional_entropy",
    "entropy",
    "feature_vector",
    "marginal_routing_distribution",
    "mutual_information",
    "normalized_mutual_information",
    "residual_identity_entropy",
    "resolve_identity",
]

#: Softmax temperature for the confusion matrix (higher = more confusion).
CONFUSION_TEMPERATURE = 1.0

#: Canonical task -> jurisdiction mapping (declared domain data; tasks in
#: ``coordination_farce.TASK_CATALOG`` carry no jurisdiction field).
TASK_JURISDICTIONS: dict[str, str] = {
    "baccarat": "gambling",
    "burn_baccarat": "field ops",
    "smersh_hq": "field ops",
    "casino_vault": "security",
    "mata_bond": "seduction",
    "gamma_ray": "diplomacy",
}

#: Bayesian likelihood table (deterministic; documented constants).
LIKELIHOOD_JURISDICTION_MATCH = 0.9
LIKELIHOOD_JURISDICTION_MISS = 0.2
LIKELIHOOD_CLEARANCE_OK = 0.95
LIKELIHOOD_CLEARANCE_SHORT = 0.4

_JURISDICTIONS: tuple[str, ...] = tuple(sorted({agent.jurisdiction for agent in AGENT_ROSTER}))


def feature_vector(agent: Agent) -> np.ndarray:
    """Deterministic feature vector: normalized clearance + jurisdiction one-hot.

    The one-hot spans :data:`_JURISDICTIONS` — the sorted distinct
    jurisdictions of :data:`AGENT_ROSTER` — so the vector has
    ``1 + len(_JURISDICTIONS)`` entries (six for the canonical five-Bond
    roster, whose jurisdictions are all distinct).

    Args:
        agent: a roster agent.

    Returns:
        A float array of shape ``(1 + len(_JURISDICTIONS),)``:
        ``[clearance / 5, one-hot over roster jurisdictions]``.
    """
    one_hot = np.zeros(len(_JURISDICTIONS), dtype=float)
    one_hot[_JURISDICTIONS.index(agent.jurisdiction)] = 1.0
    return np.concatenate((np.array([agent.clearance / 5.0]), one_hot))


def build_confusion_matrix(
    agents: tuple[Agent, ...] = AGENT_ROSTER,
    *,
    temperature: float = CONFUSION_TEMPERATURE,
) -> np.ndarray:
    """Build the 5x5 routing confusion matrix.

    ``confusion[i, j]`` is the probability that an order intended for agent
    ``i`` is routed to agent ``j``: a row-softmax over pairwise feature
    similarity ``feature_i . feature_j`` scaled by ``1/temperature``.

    Args:
        agents: the roster (default: the five Bonds).
        temperature: softmax temperature (> 0).

    Returns:
        A row-stochastic ``(n, n)`` float matrix.

    Raises:
        ValueError: if ``temperature`` is not positive.
    """
    if temperature <= 0:
        raise ValueError("temperature must be > 0")
    features = np.stack([feature_vector(agent) for agent in agents])
    scores = features @ features.T
    scaled = scores / temperature
    shifted = scaled - scaled.max(axis=1, keepdims=True)
    exp = np.exp(shifted)
    return exp / exp.sum(axis=1, keepdims=True)  # type: ignore[no-any-return]


def entropy(probabilities: tuple[float, ...]) -> float:
    """Shannon entropy in bits of a discrete distribution.

    Args:
        probabilities: non-negative weights summing to 1 (or any positive
            measure; zeros are ignored).

    Returns:
        ``-sum(p log2 p)`` in bits (``0.0`` for a point mass).
    """
    return float(-sum(p * math.log2(p) for p in probabilities if p > 0.0))


def _row_entropies(confusion: np.ndarray) -> np.ndarray:
    """Per-row Shannon entropy of a row-stochastic matrix (bits)."""
    positive = np.where(confusion > 0, confusion, 1.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        terms = confusion * np.log2(positive)
    return -terms.sum(axis=1)  # type: ignore[no-any-return]


def conditional_entropy(confusion: np.ndarray, prior: tuple[float, ...]) -> float:
    """Expected entropy of routing given intent: ``H(routed | intended)``.

    This is the **dispatch ambiguity**: knowing exactly which Bond an order was
    meant for, this many bits of uncertainty remain about which Bond it
    actually reaches. It is *not* the residual uncertainty about the intended
    identity given an observed routing — that is the other direction,
    :func:`residual_identity_entropy`, and the two are equal only when the two
    marginals coincide.

    Args:
        confusion: row-stochastic confusion matrix.
        prior: prior distribution over intended agents.

    Returns:
        ``sum_i prior_i * H(routed | i)`` in bits.
    """
    row_entropies = _row_entropies(confusion)
    return float(sum(p * row_entropies[i] for i, p in enumerate(prior)))


def residual_identity_entropy(confusion: np.ndarray, prior: tuple[float, ...]) -> float:
    """Reverse conditional entropy ``H(intended | routed) = H(intended) - I``.

    The bits of *intended* identity still unresolved after the routing has been
    observed — the quantity that subtracts from the prior entropy. Writing
    ``H(intended) - I`` and then labelling the difference "ambiguity" is only
    correct for this direction; the forward direction
    (:func:`conditional_entropy`) subtracts from ``H(routed)`` instead.

    Args:
        confusion: row-stochastic confusion matrix.
        prior: prior distribution over intended agents.

    Returns:
        ``H(intended) - I(intended; routed)`` in bits.
    """
    return float(entropy(prior) - mutual_information(confusion, prior))


def marginal_routing_distribution(confusion: np.ndarray, prior: tuple[float, ...]) -> np.ndarray:
    """Marginal routing distribution ``P(routed) = prior @ confusion``."""
    return np.asarray(prior) @ confusion  # type: ignore[no-any-return]


def mutual_information(confusion: np.ndarray, prior: tuple[float, ...]) -> float:
    """Mutual information between intended and routed identity, in bits.

    ``I = H(routed) - H(routed | intended)`` — how much the observed routing
    reveals about which physical Bond was intended.
    """
    routing = marginal_routing_distribution(confusion, prior)
    h_routed = entropy(tuple(float(p) for p in routing))
    return float(h_routed - conditional_entropy(confusion, prior))


def normalized_mutual_information(confusion: np.ndarray, prior: tuple[float, ...]) -> float:
    """Normalized mutual information in ``[0, 1]``.

    Denominator is ``max(H(intended), H(routed))``; ``0`` = routing is
    independent of intent (total confusion), ``1`` = perfect routing.
    """
    routing = marginal_routing_distribution(confusion, prior)
    h_intended = entropy(prior)
    h_routed = entropy(tuple(float(p) for p in routing))
    denominator = max(h_intended, h_routed)
    if denominator <= 0.0:
        return 0.0
    return float(mutual_information(confusion, prior) / denominator)


def _likelihood(agent: Agent, task: Task, evidence: tuple[bool, bool]) -> float:
    """P(evidence | agent intended), independent jurisdiction/clearance terms."""
    jurisdiction_match, clearance_ok = evidence
    p_jurisdiction = (
        LIKELIHOOD_JURISDICTION_MATCH
        if agent.jurisdiction == TASK_JURISDICTIONS[task.task_id]
        else LIKELIHOOD_JURISDICTION_MISS
    )
    p_clearance = LIKELIHOOD_CLEARANCE_OK if agent.clearance >= task.required_clearance else LIKELIHOOD_CLEARANCE_SHORT
    p_jm = p_jurisdiction if jurisdiction_match else 1.0 - p_jurisdiction
    p_co = p_clearance if clearance_ok else 1.0 - p_clearance
    return p_jm * p_co


@dataclass(frozen=True)
class IdentityResolution:
    """Bayesian identity resolution of a single dispatch sighting."""

    task_id: str
    evidence: tuple[bool, bool]
    posterior: dict[str, float]  # agent_id -> posterior probability
    resolution: str  # argmax agent id
    confidence: float  # posterior mass of the argmax


def resolve_identity(
    task_id: str,
    evidence: tuple[bool, bool],
    *,
    agents: tuple[Agent, ...] = AGENT_ROSTER,
    tasks: tuple[Task, ...] = TASK_CATALOG,
) -> IdentityResolution:
    """Resolve which physical Bond a sighting corresponds to (Bayes).

    Uniform prior over the roster; likelihood from
    :func:`_likelihood` (jurisdiction match + clearance sufficiency against
    the task). Posterior is normalized over candidates; the argmax is the
    resolution, its mass the confidence.

    Args:
        task_id: the order's task (must exist in ``tasks``).
        evidence: ``(jurisdiction_match, clearance_ok)`` observed at dispatch.
        agents: roster (default: the five Bonds).
        tasks: task catalog (default: the film's catalog).

    Returns:
        A frozen :class:`IdentityResolution`.

    Raises:
        ValueError: if ``task_id`` is unknown.
    """
    task = next((t for t in tasks if t.task_id == task_id), None)
    if task is None:
        raise ValueError(f"unknown task id {task_id!r}")
    if not agents:
        raise ValueError("roster must not be empty")
    prior = 1.0 / len(agents)
    posterior: dict[str, float] = {agent.agent_id: prior * _likelihood(agent, task, evidence) for agent in agents}
    total = sum(posterior.values())
    posterior = {aid: p / total for aid, p in posterior.items()}
    # Explicit traversal-order argmax (dict.get returns Optional for mypy).
    resolution = max(posterior, key=lambda aid: float(posterior[aid]))
    return IdentityResolution(
        task_id=task_id,
        evidence=evidence,
        posterior=posterior,
        resolution=resolution,
        confidence=posterior[resolution],
    )


@dataclass(frozen=True)
class IdentityReport:
    """Deterministic identity-failure metrics for the five-Bond farce."""

    prior_entropy: float  # H(intended) with uniform prior, bits
    codename_entropy: float  # H(codename): 0.0 — every Bond shares the name
    conditional_entropy: float  # H(routed | intended): dispatch ambiguity, bits
    residual_identity_entropy: float  # H(intended | routed) = prior - MI, bits
    routing_entropy: float  # H(routed), bits
    mutual_information: float  # I(intended; routed), bits
    normalized_mutual_information: float  # NMI in [0, 1]
    resolution: IdentityResolution


def analyze_identity(
    task_id: str = "smersh_hq",
    evidence: tuple[bool, bool] = (True, True),
    *,
    agents: tuple[Agent, ...] = AGENT_ROSTER,
    tasks: tuple[Task, ...] = TASK_CATALOG,
) -> IdentityReport:
    """Compute the canonical identity-failure report.

    Args:
        task_id: the canonical order's task.
        evidence: the canonical sighting evidence.
        agents: roster (default: the five Bonds).
        tasks: task catalog (default: the film's catalog).

    Returns:
        A frozen :class:`IdentityReport` with every metric above.
    """
    confusion = build_confusion_matrix(agents)
    prior = tuple(1.0 / len(agents) for _ in agents)

    h_intended = entropy(prior)
    h_conditional = conditional_entropy(confusion, prior)
    routing = marginal_routing_distribution(confusion, prior)
    h_routed = entropy(tuple(float(p) for p in routing))
    mi = mutual_information(confusion, prior)
    nmi = normalized_mutual_information(confusion, prior)

    resolution = resolve_identity(task_id, evidence, agents=agents, tasks=tasks)

    return IdentityReport(
        prior_entropy=h_intended,
        codename_entropy=0.0,  # all five agents share the codename "James Bond"
        conditional_entropy=h_conditional,
        residual_identity_entropy=h_intended - mi,
        routing_entropy=h_routed,
        mutual_information=mi,
        normalized_mutual_information=nmi,
        resolution=resolution,
    )
