"""Tests for the identity-confusion model (information theory + Bayes)."""

from __future__ import annotations

import math

import numpy as np
import pytest

from casino_royale_1967.coordination_farce import AGENT_ROSTER
from casino_royale_1967.identity_confusion import (
    LIKELIHOOD_CLEARANCE_OK,
    LIKELIHOOD_JURISDICTION_MATCH,
    analyze_identity,
    build_confusion_matrix,
    conditional_entropy,
    entropy,
    feature_vector,
    marginal_routing_distribution,
    mutual_information,
    normalized_mutual_information,
    residual_identity_entropy,
    resolve_identity,
)


def _uniform(n: int) -> tuple[float, ...]:
    return tuple(1.0 / n for _ in range(n))


class TestEntropyFunctions:
    """Shannon entropy in bits."""

    def test_uniform_entropy_bits(self) -> None:
        assert entropy(_uniform(5)) == pytest.approx(math.log2(5))

    def test_point_mass_zero(self) -> None:
        assert entropy((1.0, 0.0)) == pytest.approx(0.0)

    def test_fair_coin(self) -> None:
        assert entropy((0.5, 0.5)) == pytest.approx(1.0)

    def test_zeros_ignored(self) -> None:
        assert entropy((0.5, 0.5, 0.0, 0.0)) == pytest.approx(1.0)

    def test_symmetric(self) -> None:
        assert entropy((0.8, 0.2)) == pytest.approx(entropy((0.2, 0.8)))


class TestConfusionMatrix:
    """The routing confusion matrix is row-stochastic and deterministic."""

    def test_row_stochastic(self) -> None:
        confusion = build_confusion_matrix()
        assert confusion.shape == (5, 5)
        assert np.allclose(confusion.sum(axis=1), 1.0)

    def test_diagonal_dominant(self) -> None:
        confusion = build_confusion_matrix()
        for i in range(5):
            assert confusion[i, i] == confusion[i].max()

    def test_deterministic(self) -> None:
        assert np.array_equal(build_confusion_matrix(), build_confusion_matrix())

    def test_nonpositive_temperature_raises(self) -> None:
        with pytest.raises(ValueError, match="temperature"):
            build_confusion_matrix(temperature=0.0)

    def test_feature_vector_shape(self) -> None:
        assert feature_vector(AGENT_ROSTER[0]).shape == (6,)


class TestIdentityMetrics:
    """Entropy / NMI quantify the identity-failure farce."""

    def test_canonical_metrics(self) -> None:
        confusion = build_confusion_matrix()
        prior = _uniform(len(AGENT_ROSTER))
        assert conditional_entropy(confusion, prior) == pytest.approx(2.1348, abs=1e-3)
        assert mutual_information(confusion, prior) == pytest.approx(0.1748, abs=1e-3)
        assert normalized_mutual_information(confusion, prior) == pytest.approx(0.0753, abs=1e-3)

    def test_the_two_conditional_entropies_are_different_numbers(self) -> None:
        """``H(routed|intended)`` is not ``H(intended) - I``.

        The manuscript once wrote the dispatch ambiguity and then "derived" it
        as prior minus mutual information, which silently swapped directions
        and produced a paragraph whose own arithmetic did not close. The two
        quantities differ here by more than a hundredth of a bit, which is
        enough to show at the printed precision.
        """
        confusion = build_confusion_matrix()
        prior = _uniform(len(AGENT_ROSTER))

        forward = conditional_entropy(confusion, prior)
        reverse = residual_identity_entropy(confusion, prior)
        mi = mutual_information(confusion, prior)

        # Each conditional entropy subtracts MI from *its own* marginal.
        routing = marginal_routing_distribution(confusion, prior)
        h_routed = entropy(tuple(float(p) for p in routing))
        assert forward == pytest.approx(h_routed - mi, abs=1e-9)
        assert reverse == pytest.approx(entropy(prior) - mi, abs=1e-9)

        assert forward != pytest.approx(reverse, abs=1e-2)
        assert reverse == pytest.approx(2.1471, abs=1e-3)

    def test_symmetric_case_makes_the_two_directions_agree(self) -> None:
        """Positive control: equal marginals, equal conditional entropies.

        Without this, the inequality above could be read as a property of the
        formulas rather than of this particular confusion matrix.
        """
        confusion = np.array([[0.7, 0.3], [0.3, 0.7]])
        prior = _uniform(2)
        assert conditional_entropy(confusion, prior) == pytest.approx(
            residual_identity_entropy(confusion, prior), abs=1e-9
        )

    def test_conditional_entropy_within_bounds(self) -> None:
        confusion = build_confusion_matrix()
        prior = _uniform(len(AGENT_ROSTER))
        c = conditional_entropy(confusion, prior)
        assert 0.0 <= c <= math.log2(len(AGENT_ROSTER))

    def test_marginal_is_normalized(self) -> None:
        confusion = build_confusion_matrix()
        prior = _uniform(len(AGENT_ROSTER))
        assert np.isclose(marginal_routing_distribution(confusion, prior).sum(), 1.0)

    def test_perfect_routing_nmi_one(self) -> None:
        prior = _uniform(5)
        assert normalized_mutual_information(np.eye(5), prior) == pytest.approx(1.0)

    def test_maximally_confused_nmi_zero(self) -> None:
        prior = _uniform(5)
        assert normalized_mutual_information(np.full((5, 5), 0.2), prior) == pytest.approx(0.0)


class TestBayesianResolution:
    """Posterior identity resolution of a dispatch sighting."""

    def test_canonical_resolves_to_cooper(self) -> None:
        resolution = resolve_identity("smersh_hq", (True, True))
        assert resolution.resolution == "bond_cooper"
        assert resolution.confidence == pytest.approx(0.6129, abs=1e-3)

    def test_posterior_normalizes(self) -> None:
        resolution = resolve_identity("smersh_hq", (True, True))
        assert sum(resolution.posterior.values()) == pytest.approx(1.0)

    def test_unknown_task_raises(self) -> None:
        with pytest.raises(ValueError, match="unknown task"):
            resolve_identity("moonraker", (True, True))

    def test_empty_roster_raises(self) -> None:
        from casino_royale_1967.coordination_farce import TASK_CATALOG

        with pytest.raises(ValueError, match="roster must not be empty"):
            resolve_identity("smersh_hq", (True, True), agents=(), tasks=TASK_CATALOG)

    def test_update_posterior_masses(self) -> None:
        resolution = resolve_identity("baccarat", (True, False))
        assert sum(resolution.posterior.values()) == pytest.approx(1.0)

    def test_likelihood_constants_in_unit_interval(self) -> None:
        assert 0.0 < LIKELIHOOD_JURISDICTION_MATCH < 1.0
        assert 0.0 < LIKELIHOOD_CLEARANCE_OK < 1.0


class TestDegenerateInfoMetrics:
    """Single-agent edge cases keep NMI well-defined."""

    def test_single_agent_state_nmi_is_zero(self) -> None:
        # A 1x1 identity confusion matrix has zero denominator -> NMI 0.
        confusion = np.eye(1)
        prior = _uniform(1)
        assert normalized_mutual_information(confusion, prior) == pytest.approx(0.0)


class TestIdentityReport:
    """The canonical report ties the metrics together."""

    def test_report_fields(self) -> None:
        report = analyze_identity()
        assert report.prior_entropy == pytest.approx(math.log2(5))
        assert report.codename_entropy == pytest.approx(0.0)  # all share the name
        assert report.conditional_entropy >= report.mutual_information >= 0.0
        assert report.resolution.resolution == "bond_cooper"

    def test_report_carries_both_conditional_entropies(self) -> None:
        """Both directions are first-class fields, so neither can be implied."""
        report = analyze_identity()
        assert report.residual_identity_entropy == pytest.approx(
            report.prior_entropy - report.mutual_information, abs=1e-9
        )
        assert report.conditional_entropy == pytest.approx(report.routing_entropy - report.mutual_information, abs=1e-9)
        assert report.residual_identity_entropy != pytest.approx(report.conditional_entropy, abs=1e-2)

    def test_deterministic(self) -> None:
        assert analyze_identity() == analyze_identity()
