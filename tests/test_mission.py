"""Tests for the FROZEN bond_api MissionProvider adapter (FIVE 00s).

Exercises the real provider against the real ``bond_api`` protocol: protocol
conformance, the full five-stage flow, deterministic outcomes, gadget
registration, serialization round-trips, and slug discovery. No mocks.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from bond_api.discovery import load_provider
from bond_api.protocol import (
    Debrief,
    MissionBrief,
    MissionOutcome,
    MissionPlan,
    MissionProvider,
    Provenance,
    ReconReport,
    ReconRequest,
    run_mission,
)
from bond_api.registry import GadgetRegistry, MissionRegistry
from bond_api.serialization import from_json, to_json

from casino_royale_1967.mission import (
    CODENAME,
    FILM,
    GADGETS,
    GADGET_REGISTRY,
    IDENTITY,
    PACKAGE_VERSION,
    SEED,
    MissionProvider as FilmProvider,
    register_gadgets,
)

_SRC = Path(__file__).resolve().parent.parent / "src"


class TestProtocolConformance:
    """The provider structurally satisfies the frozen MissionProvider protocol."""

    def test_is_runtime_checkable_provider(self) -> None:
        provider: MissionProvider = FilmProvider()
        assert isinstance(provider, MissionProvider)

    def test_film_slug(self) -> None:
        assert FilmProvider().film == FILM == "casino_royale_1967"

    def test_identity_constants(self) -> None:
        assert IDENTITY == "Casino Royale (1967)"
        assert CODENAME == "FIVE 00s"
        assert PACKAGE_VERSION == "0.1.0"
        assert SEED == 7


class TestMissionLifecycle:
    """Each stage returns the correct protocol payload."""

    def test_brief(self) -> None:
        provider = FilmProvider()
        brief = provider.brief()
        assert isinstance(brief, MissionBrief)
        assert brief.film == FILM
        assert brief.codename == CODENAME
        assert len(brief.objectives) == 6
        assert len(brief.assets) == 4
        assert len(brief.constraints) == 2

    def test_recon(self) -> None:
        """The recon surface is pinned exactly, not by superset.

        Documentation used to claim "one Finding per concept"; the provider
        actually returns the request goal plus seven concept findings, because
        the coordination model contributes both ``overlap`` and ``conflict``.
        An inclusive ``>=`` check could never catch that drift, so the tuple is
        asserted in full and in order.
        """
        provider = FilmProvider()
        report = provider.recon(ReconRequest(goal="characterize the farce"))
        assert isinstance(report, ReconReport)
        assert tuple(f.label for f in report.findings) == (
            "goal",
            "overlap",
            "conflict",
            "dispatch",
            "doctrine",
            "identity",
            "table",
            "escalation",
        )
        assert len(report.findings) == 8
        assert report.findings[0].detail == "characterize the farce"

    def test_plan(self) -> None:
        provider = FilmProvider()
        plan = provider.plan(provider.brief())
        assert isinstance(plan, MissionPlan)
        actions = {step.action for step in plan.steps}
        assert actions == {
            "analyze_assignments",
            "simulate_dispatch",
            "analyze_doctrine",
            "analyze_identity",
            "deal_outcome_probabilities",
            "compare_doctrines",
        }

    def test_execute(self) -> None:
        provider = FilmProvider()
        outcome = provider.execute(provider.plan(provider.brief()))
        assert isinstance(outcome, MissionOutcome)
        assert outcome.success is True
        assert isinstance(outcome.provenance, Provenance)
        assert outcome.provenance.package_version == PACKAGE_VERSION
        assert outcome.provenance.seed == SEED
        assert outcome.provenance.wall_time_s == 0.0
        assert len(outcome.results["steps_completed"]) == 6

    def test_debrief(self) -> None:
        provider = FilmProvider()
        outcome = provider.execute(provider.plan(provider.brief()))
        debrief = provider.debrief(outcome)
        assert isinstance(debrief, Debrief)
        assert debrief.outcome is outcome
        assert len(debrief.lessons) >= 3

    def test_run_mission_flow(self) -> None:
        request = ReconRequest(goal="exercise every stage")
        debrief = run_mission(FilmProvider(), request)
        assert isinstance(debrief, Debrief)
        assert debrief.outcome.success is True


class TestDeterminism:
    """Outcomes and provenance are byte-reproducible."""

    def test_execute_is_deterministic(self) -> None:
        provider = FilmProvider()
        plan = provider.plan(provider.brief())
        outcome_a = provider.execute(plan)
        outcome_b = provider.execute(plan)
        assert outcome_a == outcome_b
        assert outcome_a.provenance.input_hash == outcome_b.provenance.input_hash

    def test_output_values_are_stable(self) -> None:
        provider = FilmProvider()
        results = provider.execute(provider.plan(provider.brief())).results
        coord = results["coordination"]
        assert coord["overlap_count"] == 3
        assert coord["conflict_count"] == 3
        assert coord["loss"] == 15.0
        dispatch = results["dispatch"]
        assert dispatch["dispatched"] == 5
        assert dispatch["rejected"] == 8
        assert results["doctrine"]["spoof_index"] == 45.0


class TestGadgets:
    """The film registers its gadgets on the shared registry."""

    def test_module_registry_has_seven_gadgets(self) -> None:
        assert GADGET_REGISTRY.gadgets_for(FILM) == (
            "roster",
            "coordination",
            "dispatch",
            "doctrine",
            "identity",
            "baccarat",
            "escalation",
        )

    def test_gadgets_payloads_match_mission_results(self) -> None:
        provider = FilmProvider()
        results = provider.execute(provider.plan(provider.brief())).results
        assert GADGETS["coordination"]["overlap_count"] == results["coordination"]["overlap_count"]
        assert GADGETS["dispatch"]["chaos_index"] == results["dispatch"]["chaos_index"]
        assert GADGETS["doctrine"]["spoof_index"] == results["doctrine"]["spoof_index"]
        assert GADGETS["identity"]["resolution"] == results["identity"]["resolution"]
        assert GADGETS["baccarat"]["table_bonds"] == results["baccarat"]["table_bonds"]
        assert GADGETS["escalation"]["acceleration_factor"] == results["escalation"]["acceleration_factor"]

    def test_new_result_payloads_present(self) -> None:
        provider = FilmProvider()
        results = provider.execute(provider.plan(provider.brief())).results
        assert results["identity"]["normalized_mutual_information"] == pytest.approx(0.0753, abs=1e-3)
        assert results["baccarat"]["player_probability"] == pytest.approx(0.446147, abs=1e-5)
        assert results["escalation"]["acceleration_factor"] == pytest.approx(14.045, abs=1e-2)

    def test_register_gadgets_merges_into_existing(self) -> None:
        registry = GadgetRegistry()
        registry.register("other_film", {"x": 1})
        returned = register_gadgets(registry)
        assert returned is registry
        assert registry.contains(FILM, "roster")
        assert registry.contains("other_film", "x")
        assert "other_film" in registry.films()

    def test_new_registry_from_register_gadgets(self) -> None:
        registry = register_gadgets()
        assert isinstance(registry, GadgetRegistry)
        assert registry.gadgets_for(FILM) == (
            "roster",
            "coordination",
            "dispatch",
            "doctrine",
            "identity",
            "baccarat",
            "escalation",
        )

    def test_mission_registry_registers_provider_by_slug(self) -> None:
        registry = MissionRegistry()
        registry.register(FilmProvider())
        assert FILM in registry
        assert registry.lookup(FILM).film == FILM


class TestSerialization:
    """Protocol payloads round-trip through the frozen wire format."""

    def test_brief_round_trip(self) -> None:
        provider = FilmProvider()
        brief = provider.brief()
        restored = from_json(to_json(brief), expected=MissionBrief)
        assert restored == brief

    def test_outcome_round_trip(self) -> None:
        provider = FilmProvider()
        outcome = provider.execute(provider.plan(provider.brief()))
        restored = from_json(to_json(outcome), expected=MissionOutcome)
        assert restored == outcome

    def test_plan_round_trip(self) -> None:
        provider = FilmProvider()
        plan = provider.plan(provider.brief())
        restored = from_json(to_json(plan), expected=MissionPlan)
        assert restored == plan


class TestDiscovery:
    """The film is discoverable by slug on sys.path."""

    def test_load_provider_by_slug(self) -> None:
        provider = load_provider(FILM, search_paths=[str(_SRC)])
        assert isinstance(provider, MissionProvider)
        assert provider.film == FILM

    def test_discover_autodetect(self) -> None:
        from bond_api.discovery import discover

        found = discover(search_paths=[str(_SRC)])
        assert FILM in found
        assert found[FILM].film == FILM

    def test_protocol_surface_flat(self) -> None:
        from bond_api.protocol import protocol_surface

        surface = protocol_surface()
        assert "MissionBrief" in surface["dataclasses"]
        assert surface["provider_methods"] == ("brief", "recon", "plan", "execute", "debrief")
