from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Classification:
    opportunity_class: str
    score: int
    confidence: float
    reason: str


NEGATIVE_MARKERS = (
    "transfer",
    "change of licensee",
    "change of licence",
    "variation",
    "extended trading",
    "change of boundaries",
    "boundary",
    "temporary",
    "limited licence",
    "single function",
    "multi-function",
    "gaming machine",
)

POSITIVE_MARKERS = (
    "new on-premises",
    "new licence",
    "small bar",
    "restaurant",
    "cafe",
    "café",
    "bar",
    "hotel",
    "fit-out",
    "fitout",
    "change of use",
    "food and drink premises",
)


def classify_text(application_type: str, description: str = "", status: str = "") -> Classification:
    text = " ".join((application_type or "", description or "", status or "")).lower()
    negatives = [m for m in NEGATIVE_MARKERS if m in text]
    positives = [m for m in POSITIVE_MARKERS if m in text]

    if negatives:
        return Classification(
            opportunity_class="existing_or_low_value",
            score=20,
            confidence=0.9,
            reason=f"Negative/maintenance application markers: {', '.join(negatives)}",
        )
    if positives:
        score = min(95, 60 + 8 * len(positives))
        return Classification(
            opportunity_class="candidate_new_venue",
            score=score,
            confidence=0.8,
            reason=f"New/opening hospitality markers: {', '.join(positives)}",
        )
    return Classification(
        opportunity_class="needs_review",
        score=50,
        confidence=0.45,
        reason="Insufficient deterministic evidence; queue for review/enrichment.",
    )
