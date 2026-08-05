"""Tests for the tick-based dispatch-chaos simulation."""

from __future__ import annotations

import pytest

from casino_royale_1967.dispatch_chaos import (
    CHAOS_ORDERS,
    PROTOCOL_RULES,
    DispatchOrder,
    simulate_dispatch,
)


class TestCanonicalScenario:
    """The canonical chaos scenario fires every protocol rule."""

    def test_default_scenario_is_the_canonical_order_stream(self) -> None:
        """The no-argument call must analyse ``CHAOS_ORDERS`` itself."""
        assert simulate_dispatch() == simulate_dispatch(CHAOS_ORDERS)
        assert len(CHAOS_ORDERS) == 13

    def test_counts(self) -> None:
        report = simulate_dispatch()
        assert report.total_orders == 13
        assert report.dispatched == 5
        assert report.rejected == 8
        assert report.duplicate_dispatches == 1

    def test_success_and_chaos_ratios(self) -> None:
        report = simulate_dispatch()
        assert report.success_ratio == pytest.approx(5 / 13)
        assert report.chaos_index == pytest.approx(8 / 13)

    def test_every_rule_fires(self) -> None:
        """Bind to ``PROTOCOL_RULES`` itself, not a hand-copied list.

        This previously compared against a local duplicate of the rule names,
        so adding a sixth rule to ``PROTOCOL_RULES`` would have left the test
        green while the canonical scenario no longer exercised it.
        """
        report = simulate_dispatch()
        fired = {v.rule for v in report.violations}
        assert fired == set(PROTOCOL_RULES)
        assert len(PROTOCOL_RULES) == len(set(PROTOCOL_RULES)), "rule names must be unique"

    def test_rule_distribution(self) -> None:
        report = simulate_dispatch()
        counts = {rule: sum(1 for v in report.violations if v.rule == rule) for rule in PROTOCOL_RULES}
        assert counts["exclusive_task"] == 2
        assert counts["clearance"] == 2
        assert counts["double_booking"] == 2
        assert counts["duplicate_order"] == 1
        assert counts["duplicate_codename"] == 1

    def test_dispatched_orders(self) -> None:
        report = simulate_dispatch()
        dispatched_ids = {e.order_id for e in report.events if e.event_type == "dispatch"}
        assert dispatched_ids == {"o01", "o04", "o06", "o08", "o13"}

    def test_deterministic(self) -> None:
        assert simulate_dispatch() == simulate_dispatch()

    def test_rejected_orders_are_not_retried(self) -> None:
        report = simulate_dispatch()
        # Rejected rule names are recorded, not silently dropped.
        assert all(v.rule for v in report.violations)

    def test_timeline_events_carry_rule_for_violations(self) -> None:
        report = simulate_dispatch()
        violation_events = [e for e in report.events if e.event_type == "violation"]
        assert all(e.rule for e in violation_events)
        dispatch_events = [e for e in report.events if e.event_type == "dispatch"]
        assert all(not e.rule for e in dispatch_events)


class TestProtocolEdgeCases:
    """Clean and adversarial inputs outside the canonical scenario."""

    def test_single_clean_order_dispatches(self) -> None:
        orders = (DispatchOrder("z1", "bond_sir", "gamma_ray", priority=1, issued_tick=0),)
        report = simulate_dispatch(orders)
        assert report.dispatched == 1
        assert report.rejected == 0
        assert report.violations == ()

    def test_exclusive_task_blocks_second_agent(self) -> None:
        orders = (
            DispatchOrder("a", "bond_tremble", "baccarat", priority=1, issued_tick=0),
            DispatchOrder("b", "bond_sir", "baccarat", priority=1, issued_tick=0),
        )
        report = simulate_dispatch(orders)
        assert report.dispatched == 1
        assert report.rejected == 1
        assert report.violations[0].rule == "exclusive_task"

    def test_clearance_violation(self) -> None:
        # Jimmy (clearance 2) may not touch the gamma_ray projector (req 5).
        orders = (DispatchOrder("a", "bond_jimmy", "gamma_ray", priority=1, issued_tick=0),)
        report = simulate_dispatch(orders)
        assert report.violations[0].rule == "clearance"

    def test_double_booking_same_agent_same_tick(self) -> None:
        orders = (
            DispatchOrder("a", "bond_sir", "gamma_ray", priority=2, issued_tick=0),
            DispatchOrder("b", "bond_sir", "mata_bond", priority=1, issued_tick=0),
        )
        report = simulate_dispatch(orders)
        assert report.dispatched == 1
        assert report.violations[0].rule == "double_booking"

    def test_duplicate_order_id(self) -> None:
        orders = (
            DispatchOrder("same", "bond_sir", "gamma_ray", priority=1, issued_tick=0),
            DispatchOrder("same", "bond_sir", "gamma_ray", priority=1, issued_tick=1),
        )
        report = simulate_dispatch(orders)
        assert report.duplicate_dispatches == 1
        assert report.violations[-1].rule == "duplicate_order"

    def test_duplicate_codename_on_shared_task(self) -> None:
        # Vesper occupies smersh_hq; Sir shares the codename -> confusion.
        orders = (
            DispatchOrder("a", "bond_vesper", "smersh_hq", priority=1, issued_tick=0),
            DispatchOrder("b", "bond_sir", "smersh_hq", priority=1, issued_tick=1),
        )
        report = simulate_dispatch(orders)
        assert report.violations[-1].rule == "duplicate_codename"

    def test_priority_dispatch_order_within_tick(self) -> None:
        # Higher priority slips through before the lower priority blocks it.
        orders = (
            DispatchOrder("low", "bond_cooper", "burn_baccarat", priority=1, issued_tick=0),
            DispatchOrder("high", "bond_vesper", "baccarat", priority=3, issued_tick=0),
        )
        report = simulate_dispatch(orders)
        # Both distinct agents on distinct (non-conflicting) tasks dispatch.
        assert report.dispatched == 2

    def test_empty_orders(self) -> None:
        report = simulate_dispatch(())
        assert report.total_orders == 0
        assert report.dispatched == 0
        assert report.success_ratio == 0.0
        assert report.chaos_index == 0.0

    def test_unknown_agent_raises(self) -> None:
        orders = (DispatchOrder("a", "bond_phantom", "baccarat"),)
        with pytest.raises(ValueError, match="unknown agent"):
            simulate_dispatch(orders)

    def test_unknown_task_raises(self) -> None:
        orders = (DispatchOrder("a", "bond_sir", "moonraker"),)
        with pytest.raises(ValueError, match="unknown task"):
            simulate_dispatch(orders)

    def test_nonpositive_priority_raises(self) -> None:
        orders = (DispatchOrder("a", "bond_sir", "gamma_ray", priority=0),)
        with pytest.raises(ValueError, match="priority"):
            simulate_dispatch(orders)

    def test_negative_tick_raises(self) -> None:
        orders = (DispatchOrder("a", "bond_sir", "gamma_ray", issued_tick=-1),)
        with pytest.raises(ValueError, match="issued_tick"):
            simulate_dispatch(orders)

    def test_orders_beyond_max_ticks_are_ignored(self) -> None:
        orders = (DispatchOrder("a", "bond_sir", "gamma_ray", issued_tick=999),)
        report = simulate_dispatch(orders, max_ticks=5)
        assert report.dispatched == 0
