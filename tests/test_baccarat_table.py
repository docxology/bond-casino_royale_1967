"""Tests for the baccarat (chemin de fer) table model.

A with-replacement brute-force cross-validation re-enumerates every draw
outcome over the 10 card values with independent per-value probabilities and
compares it to :func:`deal_outcome_probabilities` — proving the enumeration
reproduces the canonical published baccarat odds.
"""

from __future__ import annotations

from itertools import permutations

import pytest

from casino_royale_1967.baccarat_table import (
    CANONICAL_TABLE_BONDS,
    VALUES,
    banker_should_draw,
    card_value,
    deal_outcome_probabilities,
    distinct_total_probability,
    hand_collision_probability,
    hand_total,
    hand_total_probabilities,
    is_natural,
    player_should_draw,
    two_card_total_counts,
)


def _probabilities(deck: dict[int, int]) -> dict[int, float]:
    total = sum(deck.values())
    return {v: deck.get(v, 0) / total for v in VALUES}


def _brute_force_with_replacement(
    deck: dict[int, int],
) -> tuple[float, float, float]:
    """Independent infinite-deck enumeration with per-value probabilities."""
    probability = _probabilities(deck)
    player = banker = tie = 0.0

    def account(p_tot: int, b_tot: int, weight: float) -> None:
        nonlocal player, banker, tie
        if p_tot > b_tot:
            player += weight
        elif b_tot > p_tot:
            banker += weight
        else:
            tie += weight

    for p1 in VALUES:
        for b1 in VALUES:
            for p2 in VALUES:
                for b2 in VALUES:
                    opening = probability[p1] * probability[b1] * probability[p2] * probability[b2]
                    p_total = (p1 + p2) % 10
                    b_total = (b1 + b2) % 10
                    if is_natural(p_total) or is_natural(b_total):
                        account(p_total, b_total, opening)
                    elif p_total in (6, 7):
                        if banker_should_draw(b_total):
                            for v5 in VALUES:
                                account(
                                    p_total,
                                    (b_total + v5) % 10,
                                    opening * probability[v5],
                                )
                        else:
                            account(p_total, b_total, opening)
                    else:
                        for v5 in VALUES:
                            p3 = (p_total + v5) % 10
                            w5 = opening * probability[v5]
                            if banker_should_draw(b_total, v5):
                                for v6 in VALUES:
                                    account(
                                        p3,
                                        (b_total + v6) % 10,
                                        w5 * probability[v6],
                                    )
                            else:
                                account(p3, b_total, w5)
    return player, banker, tie


class TestHandRules:
    """Hand valuation, naturals, and the draw rules."""

    def test_card_value(self) -> None:
        assert card_value("A") == 1
        assert card_value("5") == 5
        assert card_value("10") == 0
        assert card_value("J") == 0
        assert card_value("K") == 0

    def test_bad_rank_raises(self) -> None:
        with pytest.raises(ValueError, match="rank"):
            card_value("X")

    def test_hand_total_mod_ten(self) -> None:
        assert hand_total((7, 8)) == 5
        assert hand_total((9, 9)) == 8
        assert hand_total((0, 0)) == 0
        assert hand_total((4, 9)) == 3

    def test_natural(self) -> None:
        assert is_natural(8) and is_natural(9)
        assert not is_natural(7)

    def test_player_draws_on_zero_to_five(self) -> None:
        assert all(player_should_draw(t) for t in range(6))
        assert not player_should_draw(6) and not player_should_draw(7)

    def test_banker_high_totals_stand(self) -> None:
        assert not banker_should_draw(7)
        assert not banker_should_draw(8)
        assert not banker_should_draw(9)

    def test_banker_low_totals_draw(self) -> None:
        assert all(banker_should_draw(t) for t in range(3))

    def test_banker_table_with_player_third(self) -> None:
        assert not banker_should_draw(3, 8)
        assert banker_should_draw(3, 7)
        assert banker_should_draw(4, 2) and not banker_should_draw(4, 1)
        assert banker_should_draw(5, 5) and not banker_should_draw(5, 3)
        assert banker_should_draw(6, 7) and not banker_should_draw(6, 5)

    def test_banker_when_player_stood(self) -> None:
        assert banker_should_draw(5, None)
        assert not banker_should_draw(6, None)

    def test_banker_table_is_exhaustive_over_the_full_domain(self) -> None:
        """Every (banker_total, player_third) pair is decided by a real rule.

        The function previously ended in an unreachable ``return False``
        fallback. This sweep pins the whole domain against the published
        chemin de fer banque table, so removing that dead branch cannot
        silently change a decision.
        """
        # Published banker draw table: banker total -> player third cards that
        # make the banker draw (Ethier 2010; Wizard of Odds).
        expected_draw_cards: dict[int, set[int]] = {
            0: set(range(10)),
            1: set(range(10)),
            2: set(range(10)),
            3: set(range(10)) - {8},
            4: {2, 3, 4, 5, 6, 7},
            5: {4, 5, 6, 7},
            6: {6, 7},
            7: set(),
            8: set(),
            9: set(),
        }
        for banker_total in range(10):
            for player_third in range(10):
                assert banker_should_draw(banker_total, player_third) == (
                    player_third in expected_draw_cards[banker_total]
                ), f"banker {banker_total} vs player third {player_third}"

    def test_banker_stand_rules_when_player_stood_are_exhaustive(self) -> None:
        """The ``player_third=None`` path: banker draws on 0-5, stands on 6-9."""
        for banker_total in range(10):
            assert banker_should_draw(banker_total, None) == (banker_total <= 5)


class TestDealOdds:
    """Deal probabilities reproduce the canonical published baccarat odds."""

    def test_canonical_values(self) -> None:
        outcome = deal_outcome_probabilities()
        assert outcome.player_probability == pytest.approx(0.446147, abs=1e-5)
        assert outcome.banker_probability == pytest.approx(0.458428, abs=1e-5)
        assert outcome.tie_probability == pytest.approx(0.095426, abs=1e-5)

    def test_probabilities_sum_to_one(self) -> None:
        outcome = deal_outcome_probabilities()
        total = outcome.player_probability + outcome.banker_probability + outcome.tie_probability
        assert total == pytest.approx(1.0)

    def test_banker_advantage(self) -> None:
        # The banker historically wins more often than the player in baccarat.
        outcome = deal_outcome_probabilities()
        assert outcome.banker_probability > outcome.player_probability

    @pytest.mark.parametrize(
        "deck",
        [
            None,
            {0: 4, 1: 2, 2: 2},
            {v: 1 for v in range(10)},
            {0: 128, **{v: 32 for v in range(1, 10)}},  # 8-deck composition
        ],
    )
    def test_matches_brute_force(self, deck: dict[int, int] | None) -> None:
        resolved = deck if deck is not None else {0: 16, **{v: 4 for v in range(1, 10)}}
        expected = _brute_force_with_replacement(resolved)
        outcome = deal_outcome_probabilities(resolved)
        assert outcome.player_probability == pytest.approx(expected[0], abs=1e-9)
        assert outcome.banker_probability == pytest.approx(expected[1], abs=1e-9)
        assert outcome.tie_probability == pytest.approx(expected[2], abs=1e-9)

    def test_deterministic(self) -> None:
        assert deal_outcome_probabilities() == deal_outcome_probabilities()


class TestHandDistributionAndCollision:
    """Two-card hand totals and the birthday-style table collision."""

    def test_two_card_counts_total(self) -> None:
        counts = two_card_total_counts()
        assert sum(counts.values()) == 52 * 51  # ordered two-card deals

    def test_two_card_counts_are_exact(self) -> None:
        # A two-card total of 9 from a single deck: (0,9),(9,0),(1,8),(8,1),
        # (2,7),(7,2),(3,6),(6,3),(4,5),(5,4) — 32 ordered for value 9.
        assert two_card_total_counts()[9] == 256

    def test_hand_total_probabilities_sum_one(self) -> None:
        probabilities = hand_total_probabilities()
        assert len(probabilities) == 10
        assert sum(probabilities) == pytest.approx(1.0)

    def test_canonical_collision_probability(self) -> None:
        """The published five-Bond figure, under the i.i.d.-across-hands model.

        This pins the approximation's value, not a no-replacement truth — see
        :meth:`test_iid_approximation_is_not_exact`.
        """
        collision = hand_collision_probability(CANONICAL_TABLE_BONDS)
        assert collision == pytest.approx(0.704017, abs=1e-4)

    def test_iid_approximation_is_not_exact(self) -> None:
        """The across-hands independence assumption is real and measurable.

        ``distinct_total_probability`` multiplies single-hand marginals as if
        the hands were independent draws. A real deal removes each dealt card
        from the shoe, so the hands are correlated. On a deck small enough to
        enumerate exhaustively (two each of values 0, 1, 2) the exact
        without-replacement answer and the approximation differ by about four
        percentage points.

        The manuscript claims that gap exists; this test is the evidence. If a
        future implementation ever became exact, the ``!=`` assertion here goes
        red and the manuscript's caveat must be revisited.
        """
        deck = {0: 2, 1: 2, 2: 2}
        cards = [value for value, count in deck.items() for _ in range(count)]

        deals = 0
        distinct = 0
        for draw in permutations(range(len(cards)), 4):
            first = (cards[draw[0]] + cards[draw[1]]) % 10
            second = (cards[draw[2]] + cards[draw[3]]) % 10
            deals += 1
            if first != second:
                distinct += 1
        exact_distinct = distinct / deals

        approximate_distinct = distinct_total_probability(2, hand_total_probabilities(deck))

        assert exact_distinct == pytest.approx(7 / 9)
        assert approximate_distinct != pytest.approx(exact_distinct, abs=1e-3)
        assert abs(exact_distinct - approximate_distinct) == pytest.approx(0.04, abs=1e-6)

    def test_collision_grows_with_hands(self) -> None:
        probabilities = hand_total_probabilities()
        two = hand_collision_probability(2, probabilities)
        five = hand_collision_probability(5, probabilities)
        assert 0.0 < two < five < 1.0

    def test_zero_hands_no_collision(self) -> None:
        assert distinct_total_probability(0, hand_total_probabilities()) == pytest.approx(1.0)

    def test_negative_hands_raises(self) -> None:
        with pytest.raises(ValueError, match="n_hands"):
            distinct_total_probability(-1, hand_total_probabilities())

    def test_collision_uses_default_distribution(self) -> None:
        with_default = hand_collision_probability(5)
        with_explicit = hand_collision_probability(5, hand_total_probabilities())
        assert with_default == pytest.approx(with_explicit)


class TestErrorBranches:
    """Empty and malformed decks fail loudly."""

    def test_empty_deck_raises(self) -> None:
        with pytest.raises(ValueError, match="at least one"):
            deal_outcome_probabilities({v: 0 for v in VALUES})

    def test_negative_count_raises(self) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            deal_outcome_probabilities({0: 4, 1: -1})

    def test_no_two_card_deals_raises(self) -> None:
        with pytest.raises(ValueError, match="two-card"):
            hand_total_probabilities({0: 1})  # single card -> no two-card deal
