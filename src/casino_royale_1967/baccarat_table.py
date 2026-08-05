"""Baccarat (chemin de fer) table model — the farce at the table.

The film's set-piece is the baccarat championship: the table where every
Bond shows up. This module models the game with real mathematics:

* **Hand valuation**: totals mod 10, naturals (8/9), and the standard
  player/banker drawing table of chemin de fer baccarat.
* **Deal odds**: :func:`deal_outcome_probabilities` enumerates every draw
  outcome (four to six cards) under the drawing rules, weighting each card by
  its value's share of the deck — the industry-standard infinite-deck
  baccarat odds computation. For the 52-card ``STANDARD_DECK`` this
  reproduces the canonical published odds (player 0.4461, banker 0.4584,
  tie 0.0954) to the shown precision.
* **The farce metric**: :func:`hand_collision_probability` — given the
  *exact* (no-replacement) marginal distribution of a two-card hand total,
  the birthday-model probability that at least two of the *n* Bonds at the
  table are dealt the same hand total. The canonical table seats all five
  Bonds.

``card_value`` maps 10/J/Q/K to 0, so a shoe is a value-count composition
``{0: 16, 1: 4, ..., 9: 4}`` for a standard 52-card deck.

Pure domain logic: stdlib only, no ``infrastructure`` / ``bond_api``
imports. Deterministic: exact enumeration, no RNG, no wall clock.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

__all__ = [
    "CANONICAL_TABLE_BONDS",
    "DealOutcome",
    "STANDARD_DECK",
    "banker_should_draw",
    "deal_outcome_probabilities",
    "distinct_total_probability",
    "hand_collision_probability",
    "hand_total",
    "hand_total_probabilities",
    "is_natural",
    "player_should_draw",
    "two_card_total_counts",
]

#: Ten card values 0..9 (10, J, Q, K all count as 0).
VALUES: tuple[int, ...] = tuple(range(10))

#: Standard 52-card shoe as a value-count composition.
STANDARD_DECK: dict[int, int] = {0: 16, **{value: 4 for value in range(1, 10)}}

#: The canonical farce table seats all five Bonds.
CANONICAL_TABLE_BONDS = 5


def card_value(rank: str) -> int:
    """Map a rank string to its baccarat value (10/J/Q/K -> 0).

    Args:
        rank: a rank like ``"A"``, ``"7"``, ``"K"``.

    Returns:
        The integer value in ``0..9``.

    Raises:
        ValueError: for an unrecognized rank.
    """
    if rank == "A":
        return 1
    if rank in {"10", "J", "Q", "K"}:
        return 0
    if rank.isdigit() and 2 <= int(rank) <= 9:
        return int(rank)
    raise ValueError(f"unknown rank {rank!r}")


def hand_total(cards: tuple[int, ...]) -> int:
    """Baccarat hand value: sum of card values mod 10.

    Args:
        cards: card values (0..9 each).

    Returns:
        The hand total in ``0..9``.
    """
    return sum(cards) % 10


def is_natural(total: int) -> bool:
    """A two-card total of 8 or 9 is a natural and ends the deal."""
    return total in (8, 9)


def player_should_draw(player_total: int) -> bool:
    """Player draws a third card on totals 0-5 (after no natural)."""
    return player_total <= 5


def banker_should_draw(banker_total: int, player_third: int | None = None) -> bool:
    """Banker draw decision per the standard chemin de fer banque table.

    ``player_third=None`` means the player stood (total 6-7); the banker then
    draws on 0-5. Otherwise the full table applies, keyed on the player's
    third card.

    Args:
        banker_total: the banker's two-card total.
        player_third: the player's drawn third card, or ``None``.

    Returns:
        Whether the banker draws.
    """
    if banker_total >= 7:
        return False
    if banker_total <= 2:
        return True
    if player_third is None:
        return banker_total <= 5
    if banker_total == 3:
        return player_third != 8
    if banker_total == 4:
        return player_third in (2, 3, 4, 5, 6, 7)
    if banker_total == 5:
        return player_third in (4, 5, 6, 7)
    if banker_total == 6:
        return player_third in (6, 7)
    return False


@dataclass(frozen=True)
class DealOutcome:
    """Exact player/banker/tie odds for a declared value distribution."""

    player_probability: float
    banker_probability: float
    tie_probability: float
    player_weight: float
    banker_weight: float
    tie_weight: float
    total_weight: float


def _deck_composition(deck: dict[int, int] | None) -> tuple[int, ...]:
    """Normalize a deck to the canonical 10-entry value-count tuple."""
    if deck is None:
        deck = STANDARD_DECK
    return tuple(int(deck.get(value, 0)) for value in VALUES)


def deal_outcome_probabilities(
    deck: dict[int, int] | None = None,
) -> DealOutcome:
    """Exact baccarat deal odds via the industry-standard infinite-deck model.

    Enumerates every draw outcome (4-6 cards) under the chemin de fer
    drawing rules, weighting each card by its value's share of the deck
    (with replacement — the standard baccarat odds computation). For the
    52-card ``STANDARD_DECK`` this reproduces the canonical published odds
    (player 0.4461, banker 0.4584, tie 0.0954; Wizard of Odds / Ethier) to
    the shown precision.

    Args:
        deck: value-count shoe composition (default: the 52-card standard).

    Returns:
        A frozen :class:`DealOutcome` with probabilities (and raw weights).

    Raises:
        ValueError: if the deck contains no cards or a negative count.
    """
    counts = _deck_composition(deck)
    total_cards = sum(counts)
    if total_cards <= 0:
        raise ValueError("deck must contain at least one card")
    if any(count < 0 for count in counts):
        raise ValueError("deck counts must be non-negative")
    probability = {value: counts[value] / total_cards for value in VALUES}

    def weight(card: int) -> float:
        return probability[card]

    def branch(p1: int, b1: int, p2: int, b2: int) -> tuple[float, float, float]:
        opening_weight = weight(p1) * weight(b1) * weight(p2) * weight(b2)
        player_total = (p1 + p2) % 10
        banker_total = (b1 + b2) % 10
        if is_natural(player_total) or is_natural(banker_total):
            return _terminal(player_total, banker_total, opening_weight)
        if player_total in (6, 7):
            if banker_should_draw(banker_total):
                total: tuple[float, float, float] = (0.0, 0.0, 0.0)
                for v5 in VALUES:
                    total = _add_weighted_float(
                        total,
                        opening_weight * weight(v5),
                        _terminal(player_total, (banker_total + v5) % 10, 1.0),
                    )
                return total
            return _terminal(player_total, banker_total, opening_weight)
        total = (0.0, 0.0, 0.0)
        for v5 in VALUES:
            player3 = (player_total + v5) % 10
            weight5 = opening_weight * weight(v5)
            if banker_should_draw(banker_total, v5):
                for v6 in VALUES:
                    total = _add_weighted_float(
                        total,
                        weight5 * weight(v6),
                        _terminal(player3, (banker_total + v6) % 10, 1.0),
                    )
            else:
                total = _add_weighted_float(total, weight5, _terminal(player3, banker_total, 1.0))
        return total

    player_weight = banker_weight = tie_weight = 0.0
    for p1 in VALUES:
        for b1 in VALUES:
            for p2 in VALUES:
                for b2 in VALUES:
                    pw, bw, tw = branch(p1, b1, p2, b2)
                    player_weight += pw
                    banker_weight += bw
                    tie_weight += tw
    total_weight = player_weight + banker_weight + tie_weight
    return DealOutcome(
        player_probability=player_weight / total_weight,
        banker_probability=banker_weight / total_weight,
        tie_probability=tie_weight / total_weight,
        player_weight=player_weight,
        banker_weight=banker_weight,
        tie_weight=tie_weight,
        total_weight=total_weight,
    )


def _terminal(player_total: int, banker_total: int, weight: float) -> tuple[float, float, float]:
    """Weighted terminal-outcome triple for a finished deal."""
    if player_total > banker_total:
        return (weight, 0.0, 0.0)
    if banker_total > player_total:
        return (0.0, weight, 0.0)
    return (0.0, 0.0, weight)


def _add_weighted_float(
    accumulator: tuple[float, float, float],
    weight: float,
    result: tuple[float, float, float],
) -> tuple[float, float, float]:
    """Accumulate ``weight * result`` into a (player, banker, tie) counter."""
    pa, ba, ta = accumulator
    pr, br, tr = result
    return (pa + weight * pr, ba + weight * br, ta + weight * tr)


def two_card_total_counts(deck: dict[int, int] | None = None) -> dict[int, int]:
    """Exact count of ordered two-card deals per hand total.

    Args:
        deck: value-count shoe composition (default: the 52-card standard).

    Returns:
        Mapping ``total -> count of ordered 2-card deals`` (without
        replacement within the hand).
    """
    counts = _deck_composition(deck)
    totals: dict[int, int] = {value: 0 for value in VALUES}
    for first, first_count in enumerate(counts):
        for second, second_count in enumerate(counts):
            ways = first_count * (second_count - (1 if first == second else 0))
            if ways > 0:
                totals[(first + second) % 10] += ways
    return totals


def hand_total_probabilities(
    deck: dict[int, int] | None = None,
) -> tuple[float, ...]:
    """Marginal distribution of a single two-card hand total (10 entries).

    Args:
        deck: value-count shoe composition (default: the 52-card standard).

    Returns:
        ``P(total)`` for totals 0..9, from the exact two-card counts.
    """
    totals = two_card_total_counts(deck)
    total_deals = sum(totals.values())
    if total_deals <= 0:
        raise ValueError("deck has no possible two-card deals")
    return tuple(totals[value] / total_deals for value in VALUES)


def distinct_total_probability(n_hands: int, probabilities: tuple[float, ...]) -> float:
    """Birthday-model probability that ``n_hands`` totals are all distinct.

    Uses the elementary symmetric polynomial ``e_n`` of the hand-total
    distribution: ``P(all distinct) = n! * e_n(p_0..p_9)`` under the
    documented i.i.d. approximation across hands (within a hand the deal is
    exact and without replacement).

    Args:
        n_hands: number of Bonds at the table.
        probabilities: hand-total distribution (10 entries summing to 1).

    Returns:
        Probability in ``[0, 1]``.
    """
    if n_hands < 0:
        raise ValueError("n_hands must be non-negative")
    if n_hands == 0:
        return 1.0
    elementary: list[float] = [0.0] * (n_hands + 1)
    elementary[0] = 1.0
    for probability in probabilities:
        for degree in range(min(n_hands, 10), 0, -1):
            elementary[degree] += probability * elementary[degree - 1]
    return float(math.factorial(n_hands) * elementary[n_hands])


def hand_collision_probability(
    n_hands: int,
    probabilities: tuple[float, ...] | None = None,
) -> float:
    """Probability at least two of ``n_hands`` Bonds share a hand total.

    Args:
        n_hands: Bonds seated at the table.
        probabilities: hand-total distribution (default: exact 52-card).

    Returns:
        ``1 - P(all totals distinct)`` in ``[0, 1]``.
    """
    if probabilities is None:
        probabilities = hand_total_probabilities()
    return float(1.0 - distinct_total_probability(n_hands, probabilities))
