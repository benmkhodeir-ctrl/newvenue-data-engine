from __future__ import annotations

from dataclasses import dataclass
import re
from collections import defaultdict
from typing import Iterable

TRUST_WEIGHTS = {
    "government": 30,
    "planning_application": 28,
    "liquor_application": 26,
    "official_venue": 24,
    "official_operator": 24,
    "leasing_announcement": 20,
    "reputable_news": 18,
    "industry_press": 16,
    "social_profile": 12,
    "directory": 6,
    "search_result": 3,
}


def _clean(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (value or "").casefold()).strip()


def _tokens(value: str) -> set[str]:
    return {token for token in _clean(value).split() if len(token) > 1}


def _similarity(a: str, b: str) -> float:
    left, right = _tokens(a), _tokens(b)
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


@dataclass(frozen=True)
class Evidence:
    operator_name: str
    source_url: str
    source_type: str
    address: str = ""
    tenancy: str = ""
    venue_name: str = ""
    evidence_text: str = ""
    named_person: str = ""
    public_contact: str = ""


@dataclass(frozen=True)
class Resolution:
    operator_name: str | None
    score: int
    confidence: str
    reasons: tuple[str, ...]
    source_urls: tuple[str, ...]
    named_person: str | None = None
    public_contact: str | None = None


def score_evidence(evidence: Evidence, *, address: str, tenancy: str = "", venue_name: str = "") -> tuple[int, list[str]]:
    score = TRUST_WEIGHTS.get(evidence.source_type, 0)
    reasons = [f"source:{evidence.source_type}"]

    if address and _clean(evidence.address) == _clean(address):
        score += 35
        reasons.append("exact_address")
    else:
        similarity = _similarity(evidence.address, address)
        if similarity >= 0.8:
            score += 25
            reasons.append("strong_address_match")
        elif similarity >= 0.55:
            score += 12
            reasons.append("partial_address_match")

    if tenancy and evidence.tenancy:
        if _clean(tenancy) == _clean(evidence.tenancy):
            score += 25
            reasons.append("exact_tenancy")
        else:
            score -= 20
            reasons.append("tenancy_conflict")

    if venue_name and evidence.venue_name:
        similarity = _similarity(venue_name, evidence.venue_name)
        if similarity >= 0.8:
            score += 18
            reasons.append("strong_venue_name_match")
        elif similarity >= 0.5:
            score += 9
            reasons.append("partial_venue_name_match")

    operator_tokens = _tokens(evidence.operator_name)
    evidence_tokens = _tokens(evidence.evidence_text)
    if operator_tokens and operator_tokens <= evidence_tokens:
        score += 8
        reasons.append("operator_named_in_evidence")

    return max(score, 0), reasons


def resolve_operator(evidence_rows: Iterable[Evidence], *, address: str, tenancy: str = "", venue_name: str = "") -> Resolution:
    grouped: dict[str, list[tuple[Evidence, int, list[str]]]] = defaultdict(list)
    display_names: dict[str, str] = {}

    for evidence in evidence_rows:
        key = _clean(evidence.operator_name)
        if not key:
            continue
        display_names.setdefault(key, evidence.operator_name.strip())
        score, reasons = score_evidence(evidence, address=address, tenancy=tenancy, venue_name=venue_name)
        grouped[key].append((evidence, score, reasons))

    if not grouped:
        return Resolution(None, 0, "unknown", ("no_operator_evidence",), ())

    candidates: list[tuple[str, int, list[tuple[Evidence, int, list[str]]]]] = []
    for key, rows in grouped.items():
        best = max(score for _, score, _ in rows)
        independent_sources = len({row.source_url for row, _, _ in rows})
        source_types = len({row.source_type for row, _, _ in rows})
        corroboration_bonus = min(max(independent_sources - 1, 0) * 10, 20)
        diversity_bonus = min(max(source_types - 1, 0) * 5, 10)
        candidates.append((key, best + corroboration_bonus + diversity_bonus, rows))

    candidates.sort(key=lambda item: item[1], reverse=True)
    winner_key, winner_score, winner_rows = candidates[0]
    runner_up_score = candidates[1][1] if len(candidates) > 1 else 0
    margin = winner_score - runner_up_score
    independent_sources = len({row.source_url for row, _, _ in winner_rows})

    if winner_score >= 80 and margin >= 20 and independent_sources >= 2:
        confidence = "confirmed"
    elif winner_score >= 65 and margin >= 15:
        confidence = "strong"
    elif winner_score >= 45 and margin >= 10:
        confidence = "probable"
    else:
        confidence = "unknown"

    if confidence == "unknown":
        return Resolution(None, winner_score, confidence, (f"insufficient_margin_or_score:{margin}",), tuple(sorted({row.source_url for row, _, _ in winner_rows})))

    best_row = max(winner_rows, key=lambda item: item[1])
    reasons = list(best_row[2])
    if independent_sources > 1:
        reasons.append(f"corroborated_sources:{independent_sources}")
    if margin:
        reasons.append(f"candidate_margin:{margin}")

    named_person = next((row.named_person for row, _, _ in winner_rows if row.named_person), None)
    public_contact = next((row.public_contact for row, _, _ in winner_rows if row.public_contact), None)
    return Resolution(display_names[winner_key], winner_score, confidence, tuple(reasons), tuple(sorted({row.source_url for row, _, _ in winner_rows})), named_person, public_contact)
