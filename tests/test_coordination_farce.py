"""Tests for the coordination-failure model (five overlapping Bonds)."""

from __future__ import annotations

import pytest

from casino_royale_1967.coordination_farce import (
    AGENT_ROSTER,
    DEFAULT_ASSIGNMENTS,
    TASK_CATALOG,
    analyze_assignments,
    deduplicate_assignments,
)


class TestRosterAndCatalog:
    """The five Bonds and their shared codename — the model's premise."""

    def test_five_agents(self) -> None:
        assert len(AGENT_ROSTER) == 5

    def test_all_share_codename(self) -> None:
        assert {a.codename for a in AGENT_ROSTER} == {"James Bond"}

    def test_actors_match_the_1967_film(self) -> None:
        aliases = {a.alias for a in AGENT_ROSTER}
        assert aliases == {
            "David Niven",
            "Peter Sellers",
            "Ursula Andress",
            "Woody Allen",
            "Terence Cooper",
        }

    def test_clearance_levels_are_distinct(self) -> None:
        assert {a.clearance for a in AGENT_ROSTER} == {5, 3, 4, 2, 4}


class TestAnalyzeAssignments:
    """Overlap, conflict, clearance, and weighted loss detection."""

    def test_canonical_report_values(self) -> None:
        report = analyze_assignments(DEFAULT_ASSIGNMENTS)
        assert report.total_assignments == 8
        assert report.overlap_count == 3
        assert report.conflict_count == 3
        assert len(report.clearance_violations) == 1
        assert report.loss == 15.0

    def test_overlap_victims_are_the_extra_bonds(self) -> None:
        report = analyze_assignments(DEFAULT_ASSIGNMENTS)
        # Victims are the extras beyond the lexicographically-first agent.
        assert report.overlap_victims["baccarat"] == ("bond_tremble", "bond_vesper")
        assert report.overlap_victims["smersh_hq"] == ("bond_vesper",)

    def test_per_task_load(self) -> None:
        report = analyze_assignments(DEFAULT_ASSIGNMENTS)
        assert report.per_task_load["baccarat"] == 3
        assert report.per_task_load["burn_baccarat"] == 1

    def test_single_clean_assignment_has_no_failures(self) -> None:
        report = analyze_assignments(
            (DEFAULT_ASSIGNMENTS[0],)  # tremble -> baccarat only
        )
        assert report.overlap_count == 0
        assert report.conflict_count == 0
        assert report.loss == 0.0

    def test_custom_weights_change_loss_but_not_counts(self) -> None:
        base = analyze_assignments(DEFAULT_ASSIGNMENTS)
        heavy = analyze_assignments(
            DEFAULT_ASSIGNMENTS, overlap_weight=5.0, conflict_weight=7.0
        )
        assert heavy.overlap_count == base.overlap_count
        assert heavy.conflict_count == base.conflict_count
        assert heavy.loss == 5.0 * 3 + 7.0 * 3

    def test_conflict_detection_between_conflicting_tasks(self) -> None:
        # Vesper on baccarat AND Cooper on burn_baccarat => one conflict pair.
        report = analyze_assignments(
            (
                DEFAULT_ASSIGNMENTS[2],  # vesper -> baccarat
                DEFAULT_ASSIGNMENTS[3],  # cooper -> burn_baccarat
            )
        )
        assert report.conflict_count == 1

    def test_unknown_agent_id_raises(self) -> None:
        from casino_royale_1967.coordination_farce import Assignment

        bad = (Assignment(agent_id="bond_phantom", task_id="baccarat"),)
        with pytest.raises(ValueError, match="unknown agent"):
            analyze_assignments(bad)

    def test_unknown_task_id_raises(self) -> None:
        from casino_royale_1967.coordination_farce import Assignment

        bad = (Assignment(agent_id="bond_sir", task_id="moon_raker"),)
        with pytest.raises(ValueError, match="unknown task"):
            analyze_assignments(bad)

    def test_same_agent_twice_on_one_task_is_not_overlap(self) -> None:
        from casino_royale_1967.coordination_farce import Assignment

        report = analyze_assignments(
            (
                Assignment("bond_sir", "baccarat", 1),
                Assignment("bond_sir", "baccarat", 1),
            )
        )
        # Same agent duplicated: distinct set size is 1, so no overlap.
        assert report.overlap_count == 0


class TestDeduplicateAssignments:
    """Single-agent discipline removes every overlap."""

    def test_keeps_highest_priority_per_task(self) -> None:
        result = deduplicate_assignments(DEFAULT_ASSIGNMENTS)
        assert len(result.kept) == 5
        assert len(result.dropped) == 3
        # Baccarat must keep tremble (priority 3), not sir (2) or vesper (1).
        kept_baccarat = [a for a in result.kept if a.task_id == "baccarat"]
        assert [a.agent_id for a in kept_baccarat] == ["bond_tremble"]

    def test_dedup_removes_all_overlaps(self) -> None:
        """Single-agent discipline kills every overlap.

        The only residue is the irreducible cross-task clash: one agent must
        win the baccarat championship while another burns the same table, so
        a single conflict (loss = the conflict weight) remains.
        """
        original = analyze_assignments(DEFAULT_ASSIGNMENTS)
        result = deduplicate_assignments(DEFAULT_ASSIGNMENTS)
        cleaned = analyze_assignments(result.kept)
        assert original.overlap_count == 3
        assert original.conflict_count == 3
        assert cleaned.overlap_count == 0
        assert cleaned.conflict_count == 1
        assert cleaned.loss == 3.0

    def test_dropped_by_task_lists_the_victims(self) -> None:
        result = deduplicate_assignments(DEFAULT_ASSIGNMENTS)
        assert result.dropped_by_task["baccarat"] == ("bond_sir", "bond_vesper")
        assert result.dropped_by_task["smersh_hq"] == ("bond_jimmy",)

    def test_deterministic_output(self) -> None:
        assert deduplicate_assignments(DEFAULT_ASSIGNMENTS) == (
            deduplicate_assignments(DEFAULT_ASSIGNMENTS)
        )

    def test_priority_tie_breaks_by_agent_id(self) -> None:
        from casino_royale_1967.coordination_farce import Assignment

        result = deduplicate_assignments(
            (
                Assignment("bond_vesper", "mata_bond", 2),
                Assignment("bond_sir", "mata_bond", 2),
            )
        )
        # Equal priority => lexicographically greatest id wins ("bond_vesper").
        assert [a.agent_id for a in result.kept] == ["bond_vesper"]
        assert [a.agent_id for a in result.dropped] == ["bond_sir"]


class TestCoordinationContract:
    """The five-Bond coordination concept is a testable, stable model."""

    def test_all_tasks_defined_in_catalog(self) -> None:
        task_ids = {task.task_id for task in TASK_CATALOG}
        assigned_task_ids = {a.task_id for a in DEFAULT_ASSIGNMENTS}
        assert assigned_task_ids <= task_ids

    def test_conflict_graph_keys_are_in_catalog(self) -> None:
        from casino_royale_1967.coordination_farce import CONFLICT_GRAPH, TASK_BY_ID

        for pair in CONFLICT_GRAPH:
            for task_id in pair:
                assert task_id in TASK_BY_ID
