"""Escalation-ladder model — doctrine as an absorbing Markov chain.

The farce's arc is escalation: a quiet British intelligence service becomes a
rumour, a scandal, a world-famous spectacle, and finally a catastrophe. This
module models the ladder as an absorbing Markov chain whose transition matrix
is a *doctrine*: the spoof doctrine ("maximum spectacle", "anyone may shoot
anyone") pumps probability toward catastrophe; a sanctioned doctrine keeps the
ladder calm.

Real mathematics (Kemeny–Snell absorbing-chain theory, computed exactly with
deterministic numpy linear algebra):

* states ``quiet → rumour → scandal → spectacle → catastrophe`` with
  ``catastrophe`` absorbing;
* the **fundamental matrix** ``N = (I - Q)^{-1}`` over the transient states;
* **expected absorption time** from each state: ``t = N @ 1`` (the expected
  number of steps until catastrophe);
* **spectral radius** of ``Q`` (a radius < 1 guarantees absorption);
* the **escalation index** = expected steps from ``quiet``, compared across
  doctrines via :func:`compare_doctrines`.

Pure domain logic: stdlib + numpy only, no ``infrastructure`` / ``bond_api``
imports. Deterministic: LAPACK linear algebra, no RNG, no wall clock.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

__all__ = [
    "ABSORBING_STATE",
    "LADDER_STATES",
    "DoctrineComparison",
    "EscalationReport",
    "SANCTIONED_DOCTRINE_TRANSITIONS",
    "SPOOF_DOCTRINE_TRANSITIONS",
    "compare_doctrines",
    "escalation_analysis",
    "expected_absorption_times",
    "fundamental_matrix",
]

#: The escalation ladder, in order; the last state is absorbing.
LADDER_STATES: tuple[str, ...] = (
    "quiet",
    "rumour",
    "scandal",
    "spectacle",
    "catastrophe",
)
ABSORBING_STATE = "catastrophe"

#: Transition matrix under the film's spoof doctrine (row-stochastic).
SPOOF_DOCTRINE_TRANSITIONS: tuple[tuple[float, ...], ...] = (
    (0.30, 0.40, 0.20, 0.08, 0.02),
    (0.00, 0.25, 0.40, 0.25, 0.10),
    (0.00, 0.00, 0.20, 0.45, 0.35),
    (0.00, 0.00, 0.00, 0.40, 0.60),
    (0.00, 0.00, 0.00, 0.00, 1.00),
)

#: Transition matrix under a disciplined ops doctrine (row-stochastic).
SANCTIONED_DOCTRINE_TRANSITIONS: tuple[tuple[float, ...], ...] = (
    (0.70, 0.22, 0.06, 0.02, 0.00),
    (0.25, 0.55, 0.15, 0.04, 0.01),
    (0.08, 0.30, 0.45, 0.14, 0.03),
    (0.02, 0.10, 0.30, 0.48, 0.10),
    (0.00, 0.00, 0.00, 0.00, 1.00),
)


def _validate_transitions(transitions: tuple[tuple[float, ...], ...], states: tuple[str, ...]) -> tuple[int, ...]:
    """Validate a row-stochastic square matrix with one absorbing row.

    Args:
        transitions: the candidate transition matrix.
        states: the state names (its length must match the matrix size).

    Returns:
        The index of the absorbing state.

    Raises:
        ValueError: if the matrix is not square/row-stochastic, does not
            match the state count, or has no absorbing row.
    """
    size = len(states)
    if len(transitions) != size:
        raise ValueError(f"transitions must have {size} rows (one per state), got {len(transitions)}")
    absorbing_rows: list[int] = []
    for row_index, row in enumerate(transitions):
        if len(row) != size:
            raise ValueError(f"row {row_index} must have {size} entries, got {len(row)}")
        if any(entry < 0.0 for entry in row):
            raise ValueError(f"row {row_index} has a negative entry")
        if not np.isclose(sum(row), 1.0):
            raise ValueError(f"row {row_index} does not sum to 1")
        if row[row_index] == 1.0 and sum(entry for j, entry in enumerate(row) if j != row_index) == 0.0:
            absorbing_rows.append(row_index)
    if not absorbing_rows:
        raise ValueError("transitions must contain at least one absorbing state")
    return tuple(absorbing_rows)


def fundamental_matrix(
    transitions: tuple[tuple[float, ...], ...], states: tuple[str, ...] = LADDER_STATES
) -> np.ndarray:
    """The fundamental matrix ``N = (I - Q)^{-1}`` of the transient states.

    ``N[i, j]`` is the expected number of visits to transient state ``j``
    starting from transient state ``i`` before absorption.

    Args:
        transitions: a validated row-stochastic transition matrix.
        states: the state names.

    Returns:
        ``(k, k)`` float matrix, ``k`` = number of transient states.
    """
    _validate_transitions(transitions, states)
    transient = [i for i in range(len(states)) if states[i] != ABSORBING_STATE]
    matrix = np.asarray(transitions, dtype=float)
    q = matrix[np.ix_(transient, transient)]
    return np.linalg.inv(np.eye(len(transient)) - q)


def expected_absorption_times(
    transitions: tuple[tuple[float, ...], ...], states: tuple[str, ...] = LADDER_STATES
) -> tuple[float, ...]:
    """Expected number of steps to absorption from each transient state.

    ``t = N @ 1`` where ``N`` is the fundamental matrix.

    Args:
        transitions: a validated row-stochastic transition matrix.
        states: the state names.

    Returns:
        Expected absorption time per transient state, in state order.
    """
    fundamental = fundamental_matrix(transitions, states)
    ones = np.ones(fundamental.shape[0])
    return tuple(float(value) for value in (fundamental @ ones))


@dataclass(frozen=True)
class EscalationReport:
    """Deterministic absorbing-chain analysis of one doctrine."""

    states: tuple[str, ...]
    absorbing_state: str
    expected_absorption: tuple[float, ...]  # per transient state
    absorption_probability: float  # from the first (quiet) state, ~1.0
    spectral_radius_q: float  # < 1 guarantees absorption
    escalation_index: float  # expected steps from quiet to catastrophe


def escalation_analysis(
    transitions: tuple[tuple[float, ...], ...],
    states: tuple[str, ...] = LADDER_STATES,
) -> EscalationReport:
    """Analyze a doctrine's escalation ladder as an absorbing Markov chain.

    Args:
        transitions: a row-stochastic transition matrix (validated).
        states: the state names (last declared absorbing).

    Returns:
        A frozen :class:`EscalationReport`.

    Raises:
        ValueError: for an invalid transition matrix (see
            :func:`_validate_transitions`).
    """
    _validate_transitions(transitions, states)
    transient = [i for i in range(len(states)) if states[i] != ABSORBING_STATE]
    times = expected_absorption_times(transitions, states)

    matrix = np.asarray(transitions, dtype=float)
    q = matrix[np.ix_(transient, transient)]
    eigenvalues = np.linalg.eigvals(q)
    spectral_radius = float(max(abs(float(eigenvalue)) for eigenvalue in eigenvalues))

    # Absorption probability from the first state: solve the standard system.
    r = matrix[np.ix_(transient, [len(states) - 1])]
    absorption = np.linalg.solve(np.eye(len(transient)) - q, r)
    absorption_probability = float(absorption[0, 0])

    return EscalationReport(
        states=states,
        absorbing_state=ABSORBING_STATE,
        expected_absorption=times,
        absorption_probability=absorption_probability,
        spectral_radius_q=spectral_radius,
        escalation_index=times[0],
    )


@dataclass(frozen=True)
class DoctrineComparison:
    """The farce-vs-discipline escalation comparison."""

    spoof_index: float  # expected steps from quiet under the spoof doctrine
    sanctioned_index: float  # expected steps from quiet under the sane doctrine
    acceleration_factor: float  # sanctioned / spoof (> 1 = farce escalates faster)
    spoof_report: EscalationReport
    sanctioned_report: EscalationReport


def compare_doctrines() -> DoctrineComparison:
    """Compare the spoof doctrine against the sanctioned doctrine.

    Returns:
        A frozen :class:`DoctrineComparison` with both analyses and the
        acceleration factor (how many times faster the farce reaches
        catastrophe).
    """
    spoof = escalation_analysis(SPOOF_DOCTRINE_TRANSITIONS)
    sanctioned = escalation_analysis(SANCTIONED_DOCTRINE_TRANSITIONS)
    acceleration = sanctioned.escalation_index / spoof.escalation_index if spoof.escalation_index > 0.0 else 0.0
    return DoctrineComparison(
        spoof_index=spoof.escalation_index,
        sanctioned_index=sanctioned.escalation_index,
        acceleration_factor=acceleration,
        spoof_report=spoof,
        sanctioned_report=sanctioned,
    )
