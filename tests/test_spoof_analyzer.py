"""Tests for the spoof protocol analyzer (satirical ops doctrine)."""

from __future__ import annotations

import pytest

from casino_royale_1967.spoof_analyzer import (
    CANONICAL_SPOOF_DOCTRINE,
    REAL_OPS_RULES,
    analyze_doctrine,
)


class TestCanonicalDoctrine:
    """The film's standing orders score as farcical but tractable."""

    def test_directive_count(self) -> None:
        report = analyze_doctrine()
        assert report.directive_count == 8
        assert len(report.verdicts) == 8

    def test_aggregate_index(self) -> None:
        report = analyze_doctrine()
        assert report.spoof_index == pytest.approx(45.0)
        assert report.mean_score == pytest.approx(4.5)
        assert report.total_score == pytest.approx(36.0)

    def test_worst_directive(self) -> None:
        report = analyze_doctrine()
        assert report.worst_directive == "In case of doubt, blow up the table."

    def test_word_boundary_no_substring_collision(self) -> None:
        """'any' inside 'anyone' must not double-count; 'all' not in 'calling'."""
        report = analyze_doctrine()
        by_text = {v.text: v.spoof_score for v in report.verdicts}
        # Anyone -> any(1.0)+anyone(2.0)+command(2.0) = 5 old vs 4 fixed.
        assert by_text["Anyone may impersonate the chief."] == pytest.approx(4.0)
        # calling cards -> 'all' marker must not fire inside 'calling'.
        assert by_text["All agents shall carry identical calling cards."] == pytest.approx(7.0)

    def test_absolutist_directives_contradict_rules(self) -> None:
        report = analyze_doctrine()
        per_text = {v.text: v.inverted_rules for v in report.verdicts}
        assert "identity" in per_text["Every agent is James Bond."]
        assert "single_agent" in per_text["Every agent is James Bond."]
        assert per_text["Anyone may impersonate the chief."] == ("command",)
        assert per_text["In case of doubt, blow up the table."] == ("force",)

    def test_directive_scoring_breakdown(self) -> None:
        report = analyze_doctrine()
        scores = {v.text: v.spoof_score for v in report.verdicts}
        assert scores["Every agent is James Bond."] == pytest.approx(6.0)
        assert scores["Discretion: none. Spectacle: maximum."] == pytest.approx(5.0)
        assert scores["Baccarat is a matter of national security."] == pytest.approx(0.0)
        assert scores["If you meet another James Bond, shoot him."] == pytest.approx(6.5)

    def test_flags_present_for_absolutist_and_contradiction(self) -> None:
        report = analyze_doctrine()
        first = report.verdicts[0]  # "Every agent is James Bond."
        assert "absolutist" in first.flags
        assert "contradicts:identity" in first.flags

    def test_rule_violation_counts(self) -> None:
        report = analyze_doctrine()
        assert report.rule_violation_counts["identity"] == 3
        assert report.rule_violation_counts["fratricide"] == 1

    def test_deterministic(self) -> None:
        assert analyze_doctrine() == analyze_doctrine()


class TestDoctrineAnalytics:
    """Straight-faced doctrine should score near zero."""

    def test_sane_directive_scores_zero(self) -> None:
        report = analyze_doctrine(("One agent per operation.", "Verify identity."))
        assert report.spoof_index == pytest.approx(0.0)
        assert report.mean_score == pytest.approx(0.0)

    def test_all_real_rules_are_recognised(self) -> None:
        # Every real rule keyword must be matched by at least one canonical
        # directive in its inverted set — proves the analyzer actually exercises
        # the whole rule surface.
        report = analyze_doctrine()
        inverted = set().union(*(set(v.inverted_rules) for v in report.verdicts))
        expected = {key for key, _text in REAL_OPS_RULES}
        assert inverted == expected

    def test_empty_doctrine_is_well_defined(self) -> None:
        report = analyze_doctrine(())
        assert report.directive_count == 0
        assert report.spoof_index == pytest.approx(0.0)
        assert report.worst_directive == ""
        assert report.rule_violation_counts == {}

    def test_oxymoron_flag(self) -> None:
        report = analyze_doctrine(("Classified publicity for coordinated improvisation.",))
        verdict = report.verdicts[0]
        assert ("classified", "publicity") in verdict.oxymorons
        assert ("coordinated", "improvisation") in verdict.oxymorons
        assert "oxymoron" in verdict.flags

    def test_single_string_directive_is_treated_as_one(self) -> None:
        report = analyze_doctrine("Every agent is James Bond.")
        assert report.directive_count == 1
        assert report.verdicts[0].spoof_score == pytest.approx(6.0)

    def test_index_is_capped_at_100(self) -> None:
        report = analyze_doctrine(("Every anyone all none maximum blow up shoot never always.",))
        # Large marker/absolutism score must not exceed 100.
        assert report.spoof_index <= 100.0

    def test_canonical_matches_model_constants(self) -> None:
        assert len(CANONICAL_SPOOF_DOCTRINE) == 8
