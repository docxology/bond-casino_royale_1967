"""Tests for the escalation-ladder absorbing Markov chain model."""

from __future__ import annotations

import warnings

import numpy as np
import pytest

from casino_royale_1967.escalation_ladder import (
    LADDER_STATES,
    SANCTIONED_DOCTRINE_TRANSITIONS,
    SPOOF_DOCTRINE_TRANSITIONS,
    compare_doctrines,
    escalation_analysis,
    expected_absorption_times,
    fundamental_matrix,
)


class TestValidation:
    """Malformed transition matrices fail loudly."""

    def test_wrong_row_count_raises(self) -> None:
        with pytest.raises(ValueError, match="rows"):
            escalation_analysis(((0.5, 0.5), (0.5, 0.5)))

    def test_wrong_column_count_raises(self) -> None:
        with pytest.raises(ValueError, match="entries"):
            escalation_analysis(((0.5, 0.5), (0.5, 0.5), (0.5, 0.5), (0.5, 0.5), (0.5, 0.5)))

    def test_row_not_summing_to_one_raises(self) -> None:
        bad = list(SPOOF_DOCTRINE_TRANSITIONS)
        bad = list(bad)
        bad[0] = tuple(value / 2 for value in bad[0])
        with pytest.raises(ValueError, match="sum to 1"):
            escalation_analysis(tuple(bad))

    def test_no_absorbing_state_raises(self) -> None:
        # A pure cycle has no row with a 1 on the diagonal -> no absorbing state.
        size = len(LADDER_STATES)
        cycle: list[tuple[float, ...]] = []
        for i in range(size):
            row = [0.0] * size
            row[(i + 1) % size] = 1.0
            cycle.append(tuple(row))
        with pytest.raises(ValueError, match="absorbing"):
            escalation_analysis(tuple(cycle))

    def test_negative_entry_raises(self) -> None:
        # A single negative entry triggers the non-negative guard.
        bad: list[list[float]] = [list(row) for row in SPOOF_DOCTRINE_TRANSITIONS]
        bad[0][1] = -0.2
        transitions = tuple(tuple(row) for row in bad)
        with pytest.raises(ValueError, match="negative"):
            escalation_analysis(transitions)

    def test_all_absorbing_raises(self) -> None:
        """An all-absorbing chain leaves no transient state to analyse."""
        size = len(LADDER_STATES)
        identity = tuple(tuple(1.0 if i == j else 0.0 for j in range(size)) for i in range(size))
        with pytest.raises(ValueError, match="transient"):
            escalation_analysis(identity)


class TestAbsorbingSetIsDerivedFromTheMatrix:
    """The absorbing set comes from the matrix, never from a state's name.

    Regression guard: an earlier version keyed the transient split off the
    literal name ``"catastrophe"`` while validating against the matrix, so a
    ladder whose absorbing state sat anywhere else produced a singular
    ``(I - Q)`` or silently analysed the wrong column.
    """

    #: Same ladder, reversed, so the absorbing state is index 0, not the last.
    REVERSED_LADDER: tuple[str, ...] = ("collapse", "spectacle", "scandal", "rumour", "quiet")
    REVERSED_TRANSITIONS: tuple[tuple[float, ...], ...] = (
        (1.00, 0.00, 0.00, 0.00, 0.00),
        (0.60, 0.40, 0.00, 0.00, 0.00),
        (0.35, 0.45, 0.20, 0.00, 0.00),
        (0.10, 0.25, 0.40, 0.25, 0.00),
        (0.02, 0.08, 0.20, 0.40, 0.30),
    )

    def test_absorbing_state_is_reported_by_name(self) -> None:
        report = escalation_analysis(self.REVERSED_TRANSITIONS, self.REVERSED_LADDER)
        assert report.absorbing_state == "collapse"

    def test_reversed_ladder_matches_the_canonical_one(self) -> None:
        """Relabelling and reordering must not change the physics."""
        report = escalation_analysis(self.REVERSED_TRANSITIONS, self.REVERSED_LADDER)
        canonical = escalation_analysis(SPOOF_DOCTRINE_TRANSITIONS)
        # transient states are (spectacle, scandal, rumour, quiet) here vs
        # (quiet, rumour, scandal, spectacle) canonically -> reverse to compare.
        assert report.expected_absorption[::-1] == pytest.approx(canonical.expected_absorption)
        assert report.absorption_probability == pytest.approx(1.0)

    def test_multiple_absorbing_states_sum_to_certain_absorption(self) -> None:
        """Two absorbing states: total absorption probability is still 1."""
        states = ("quiet", "scandal", "exposure", "catastrophe")
        transitions = (
            (0.50, 0.30, 0.10, 0.10),
            (0.20, 0.40, 0.15, 0.25),
            (0.00, 0.00, 1.00, 0.00),
            (0.00, 0.00, 0.00, 1.00),
        )
        report = escalation_analysis(transitions, states)
        assert report.absorbing_state == "exposure"
        assert report.absorption_probability == pytest.approx(1.0)

    def test_complex_eigenvalues_report_the_largest_modulus(self) -> None:
        """A transient block with a complex eigenvalue pair still reports rho.

        A cyclic transient block makes ``eigvals`` return complex numbers. The
        spectral radius is the largest complex *modulus*. An earlier version
        computed ``max(abs(float(eigenvalue)))``, which discards the imaginary
        part with a ``ComplexWarning``; that happens to agree here because
        Perron-Frobenius guarantees a non-negative matrix attains its spectral
        radius at a real eigenvalue, so this test pins the definition rather
        than a past wrong answer, and asserts no warning is raised.
        """
        states = ("a", "b", "c", "absorbed")
        transitions = (
            (0.00, 0.80, 0.00, 0.20),
            (0.00, 0.00, 0.80, 0.20),
            (0.80, 0.00, 0.00, 0.20),
            (0.00, 0.00, 0.00, 1.00),
        )
        eigenvalues = np.linalg.eigvals(np.asarray(transitions, dtype=float)[:3, :3])
        assert np.iscomplexobj(eigenvalues) and np.abs(eigenvalues.imag).max() > 1e-9, (
            "fixture must actually produce complex eigenvalues"
        )
        with warnings.catch_warnings():
            warnings.simplefilter("error")  # a ComplexWarning would fail here
            report = escalation_analysis(transitions, states)
        assert report.spectral_radius_q == pytest.approx(float(np.abs(eigenvalues).max()))
        assert report.spectral_radius_q == pytest.approx(0.8)
        assert report.absorption_probability == pytest.approx(1.0)


class TestSpoofDoctrine:
    """The farce doctrine escalates rapidly to catastrophe."""

    def test_canonical_index(self) -> None:
        report = escalation_analysis(SPOOF_DOCTRINE_TRANSITIONS)
        assert report.escalation_index == pytest.approx(3.9901, abs=1e-3)

    def test_expected_absorption_times(self) -> None:
        report = escalation_analysis(SPOOF_DOCTRINE_TRANSITIONS)
        times = report.expected_absorption
        assert times[0] == pytest.approx(3.9901, abs=1e-3)
        assert times[1] == pytest.approx(3.056, abs=1e-3)
        assert times[-1] == pytest.approx(1.6667, abs=1e-3)
        # Monotonic: each step up the ladder gets closer to catastrophe.
        assert times[0] > times[1] > times[2] > times[3]

    def test_absorption_is_certain(self) -> None:
        report = escalation_analysis(SPOOF_DOCTRINE_TRANSITIONS)
        assert report.absorption_probability == pytest.approx(1.0)
        assert report.absorbing_state == "catastrophe"

    def test_spectral_radius_below_one(self) -> None:
        report = escalation_analysis(SPOOF_DOCTRINE_TRANSITIONS)
        assert report.spectral_radius_q < 1.0


class TestSanctionedDoctrine:
    """The disciplined doctrine keeps the ladder calm."""

    def test_canonical_index(self) -> None:
        report = escalation_analysis(SANCTIONED_DOCTRINE_TRANSITIONS)
        assert report.escalation_index == pytest.approx(56.0418, abs=1e-3)

    def test_expected_absorption_times(self) -> None:
        times = expected_absorption_times(SANCTIONED_DOCTRINE_TRANSITIONS)
        assert times[0] == pytest.approx(56.0418, abs=1e-3)
        assert times[-1] == pytest.approx(43.675, abs=1e-3)


class TestFundamentalMatrix:
    """The fundamental matrix N = (I - Q)^{-1} over transient states."""

    def test_fundamental_matrix_shape(self) -> None:
        n = fundamental_matrix(SPOOF_DOCTRINE_TRANSITIONS)
        assert n.shape == (4, 4)  # transient states only

    def test_expected_times_are_fundamental_times_ones(self) -> None:
        n = fundamental_matrix(SPOOF_DOCTRINE_TRANSITIONS)
        ones = np.ones(n.shape[0])
        direct = tuple(float(v) for v in (n @ ones))
        via = expected_absorption_times(SPOOF_DOCTRINE_TRANSITIONS)
        assert direct == pytest.approx(via)


class TestCompareDoctrines:
    """The farce escalates far faster than discretion."""

    def test_acceleration(self) -> None:
        comparison = compare_doctrines()
        assert comparison.sanctioned_index > comparison.spoof_index
        assert comparison.acceleration_factor > 1.0

    def test_acceleration_value(self) -> None:
        comparison = compare_doctrines()
        assert comparison.spoof_index == pytest.approx(3.9901, abs=1e-3)
        assert comparison.sanctioned_index == pytest.approx(56.0418, abs=1e-3)
        assert comparison.acceleration_factor == pytest.approx(comparison.sanctioned_index / comparison.spoof_index)

    def test_deterministic(self) -> None:
        assert compare_doctrines() == compare_doctrines()
