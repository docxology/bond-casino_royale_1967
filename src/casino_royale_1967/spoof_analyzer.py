"""Spoof protocol analyzer — satirical ops doctrine (Casino Royale, 1967).

The 1967 *Casino Royale* is a satire of spycraft, and its operational doctrine
is the joke: *every agent is James Bond*, *anyone may impersonate the chief*,
*in case of doubt, blow up the table*. This module measures how far a doctrine
deviates from a sane protocol — deterministically.

* :data:`REAL_OPS_RULES` — the sane doctrine: one agent per operation,
  classified identity, clearance discipline, proportional force, no
  fratricide, covert discretion.
* :data:`SPOOF_MARKERS` — absolutist/inverted directive vocabulary with
  weights (``every``, ``anyone``, ``blow up``, ``in case of doubt``, ...).
* :data:`OXYMORON_PAIRS` — doctrine phrases that self-contradict
  (``classified`` + ``publicity``, ``discreet`` + ``explosion``, ...).
* :func:`analyze_doctrine` — per-directive verdicts: marker score +
  contradicted real rules + oxymorons, then a normalised ``spoof_index`` in
  ``[0, 100]`` plus per-rule violation counts.
* :data:`CANONICAL_SPOOF_DOCTRINE` — the film's own farcical standing orders.

Pure domain logic: stdlib only, no ``infrastructure`` / ``bond_api`` imports.
Deterministic: scoring is purely lexical over fixed tables.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

__all__ = [
    "CANONICAL_SPOOF_DOCTRINE",
    "DirectiveVerdict",
    "DoctrineReport",
    "OXYMORON_PAIRS",
    "REAL_OPS_RULES",
    "SPOOF_MARKERS",
    "analyze_doctrine",
]

# The sane ops doctrine the farce inverts. (keyword, canonical rule text)
REAL_OPS_RULES: tuple[tuple[str, str], ...] = (
    ("identity", "each agent has a single classified identity"),
    ("command", "orders flow from a single point of command"),
    ("discretion", "operations are conducted with covert discretion"),
    ("force", "force is proportional and restraint is mandatory"),
    ("fratricide", "agents never fire on fellow agents"),
    ("single_agent", "one agent per operation, no overlap"),
)

# Absolutist / inverted vocabulary, weighted by how far from doctrine it is.
SPOOF_MARKERS: dict[str, float] = {
    "every": 2.0,
    "anyone": 2.0,
    "all": 1.5,
    "none": 1.5,
    "maximum": 1.5,
    "any": 1.0,
    "in case of doubt": 2.5,
    "blow up": 3.0,
    "shoot": 2.5,
    "identical": 1.5,
    "never": 1.5,
    "always": 1.5,
}

# Phrase pairs whose joint presence is self-contradictory doctrine.
OXYMORON_PAIRS: tuple[tuple[str, str], ...] = (
    ("classified", "publicity"),
    ("coordinated", "improvisation"),
    ("discreet", "explosion"),
    ("secret", "parade"),
    ("disciplined", "chaos"),
    ("silent", "fanfare"),
)

# The film's farcical standing orders, verbatim-ish.
CANONICAL_SPOOF_DOCTRINE: tuple[str, ...] = (
    "Every agent is James Bond.",
    "Anyone may impersonate the chief.",
    "Discretion: none. Spectacle: maximum.",
    "Baccarat is a matter of national security.",
    "In case of doubt, blow up the table.",
    "The casino is the battlefield; the champagne is the ammunition.",
    "All agents shall carry identical calling cards.",
    "If you meet another James Bond, shoot him.",
)


@dataclass(frozen=True)
class DirectiveVerdict:
    """Verdict for a single doctrine directive."""

    text: str
    spoof_score: float
    inverted_rules: tuple[str, ...]  # real-rule keys contradicted
    oxymorons: tuple[tuple[str, str], ...]  # self-contradicting pairs found
    flags: tuple[str, ...]  # "absolutist", "contradicts:<rule>", "oxymoron"


@dataclass(frozen=True)
class DoctrineReport:
    """Deterministic outcome of :func:`analyze_doctrine`."""

    verdicts: tuple[DirectiveVerdict, ...]
    directive_count: int
    total_score: float
    mean_score: float
    spoof_index: float  # normalised to [0, 100]
    worst_directive: str  # text of the highest-scoring directive
    rule_violation_counts: dict[str, int]  # real-rule key -> contradicted count


#: Absolutist markers that turn a discretionary rule into an absolute one.
_ABSOLUTIST_MARKERS: tuple[str, ...] = (
    "every",
    "anyone",
    "all",
    "none",
    "maximum",
    "never",
    "always",
    "blow up",
    "shoot",
)

#: Word-boundary regex per marker ("any" must not match inside "anyone").
_MARKER_PATTERNS: dict[str, re.Pattern[str]] = {
    marker: re.compile(rf"\b{re.escape(marker)}\b", re.IGNORECASE)
    for marker in {**SPOOF_MARKERS, **{m: 0.0 for m in _ABSOLUTIST_MARKERS}}
}


def _marker_hits(text: str) -> tuple[tuple[str, float], ...]:
    """Return (marker, weight) for every spoof marker present in ``text``.

    Matching is word-boundary aware so ``any`` does not fire inside ``anyone``
    and ``all`` does not fire inside ``calling``.
    """
    lowered = text.lower()
    return tuple(
        (marker, weight) for marker, weight in sorted(SPOOF_MARKERS.items()) if _MARKER_PATTERNS[marker].search(lowered)
    )


def _inverted_rules(text: str) -> tuple[str, ...]:
    """Real rules contradicted by an absolutist directive.

    A directive *inverts* a rule when it contains the rule's keyword AND an
    absolutist marker (every/anyone/all/none/maximum/never/always/blow up/
    shoot) — i.e. it turns a discretionary rule into an absolute one.
    """
    lowered = text.lower()
    absolutist = any(_MARKER_PATTERNS[marker].search(lowered) for marker in _ABSOLUTIST_MARKERS)
    if not absolutist:
        return ()
    return tuple(key for key, _rule in REAL_OPS_RULES if any(keyword in lowered for keyword in _RULE_KEYWORDS[key]))


_RULE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "identity": ("identity", "agent", "calling card", "james bond"),
    "command": ("chief", "command", "impersonate"),
    "discretion": ("discretion", "covert", "quiet"),
    "force": ("force", "blow up", "battlefield"),
    "fratricide": ("shoot", "fratricide", "fire"),
    "single_agent": ("every", "each agent", "all agents"),
}


def _oxymorons(text: str) -> tuple[tuple[str, str], ...]:
    """Self-contradicting phrase pairs present in ``text``."""
    lowered = text.lower()
    return tuple((left, right) for left, right in OXYMORON_PAIRS if left in lowered and right in lowered)


def analyze_doctrine(
    directives: tuple[str, ...] | str = CANONICAL_SPOOF_DOCTRINE,
) -> DoctrineReport:
    """Score a doctrine line-by-line and aggregate a spoof index.

    Per directive: ``spoof_score = marker_sum + 2.0 * len(inverted_rules) +
    1.5 * len(oxymorons)``. The aggregate ``spoof_index`` is the mean score
    scaled to ``[0, 100]`` (``min(100.0, mean_score * 10)``), rounded to one
    decimal. A single ``str`` is treated as a one-directive doctrine.

    Args:
        directives: the doctrine lines to score (default: the canonical film
            doctrine).

    Returns:
        A frozen :class:`DoctrineReport`.
    """
    lines: tuple[str, ...] = (directives,) if isinstance(directives, str) else directives
    verdicts: list[DirectiveVerdict] = []
    for text in lines:
        marker_sum = sum(weight for _marker, weight in _marker_hits(text))
        inverted = _inverted_rules(text)
        oxymorons = _oxymorons(text)
        score = marker_sum + 2.0 * len(inverted) + 1.5 * len(oxymorons)

        flags: list[str] = []
        if _marker_hits(text):
            flags.append("absolutist")
        flags.extend(f"contradicts:{key}" for key in inverted)
        if oxymorons:
            flags.append("oxymoron")

        verdicts.append(
            DirectiveVerdict(
                text=text,
                spoof_score=round(score, 2),
                inverted_rules=inverted,
                oxymorons=oxymorons,
                flags=tuple(flags),
            )
        )

    count = len(verdicts)
    total = sum(verdict.spoof_score for verdict in verdicts)
    mean = total / count if count else 0.0
    spoof_index = round(min(100.0, mean * 10.0), 1)

    worst = max(verdicts, key=lambda v: v.spoof_score) if verdicts else None
    worst_directive = worst.text if worst is not None else ""

    rule_violation_counts: dict[str, int] = {}
    for verdict in verdicts:
        for key in verdict.inverted_rules:
            rule_violation_counts[key] = rule_violation_counts.get(key, 0) + 1

    return DoctrineReport(
        verdicts=tuple(verdicts),
        directive_count=count,
        total_score=round(total, 2),
        mean_score=round(mean, 2),
        spoof_index=spoof_index,
        worst_directive=worst_directive,
        rule_violation_counts=rule_violation_counts,
    )
