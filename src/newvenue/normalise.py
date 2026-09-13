from __future__ import annotations

import re
from datetime import datetime

ABBREVIATIONS = {
    r"\bSTREET\b": "ST",
    r"\bROAD\b": "RD",
    r"\bAVENUE\b": "AVE",
    r"\bPARADE\b": "PDE",
    r"\bHIGHWAY\b": "HWY",
}


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value.strip())


def normalise_address(value: str | None) -> str:
    text = clean_text(value).upper()
    text = re.sub(r"[,.;]", " ", text)
    for pattern, replacement in ABBREVIATIONS.items():
        text = re.sub(pattern, replacement, text)
    text = re.sub(r"\bNSW\b", " ", text)
    text = re.sub(r"\b2\d{3}\b", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_date(value: str | None) -> str | None:
    value = clean_text(value)
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%d %b %Y", "%d %B %Y"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    return value


def first(row: dict[str, str], *aliases: str) -> str:
    lowered = {k.strip().lower(): (v or "") for k, v in row.items()}
    for alias in aliases:
        if alias.lower() in lowered and clean_text(lowered[alias.lower()]):
            return clean_text(lowered[alias.lower()])
    return ""
