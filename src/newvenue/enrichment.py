from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def queue_candidates(conn, minimum_score: int = 55) -> int:
    rows = conn.execute(
        """
        SELECT DISTINCT v.id AS venue_id
        FROM venues v
        JOIN signals s ON s.venue_id=v.id
        WHERE s.opportunity_score >= ?
        """,
        (minimum_score,),
    ).fetchall()
    tasks = (
        "operator_entity",
        "related_venues",
        "website_social",
        "public_business_contact",
        "opening_stage",
    )
    written = 0
    for row in rows:
        for idx, task in enumerate(tasks):
            cur = conn.execute(
                "INSERT OR IGNORE INTO enrichment_queue(venue_id,task_type,priority,status,created_at) VALUES(?,?,?,?,?)",
                (row["venue_id"], task, 100 - idx * 5, "pending", now()),
            )
            written += max(cur.rowcount, 0)
    conn.commit()
    return written


def ingest_enrichment_csv(conn, path: str | Path) -> tuple[int, int]:
    path = Path(path)
    seen = written = 0
    with path.open(newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            seen += 1
            venue_id = int(row["venue_id"])
            field_name = row["field_name"].strip()
            field_value = row["field_value"].strip()
            confidence = row.get("confidence", "probable").strip().lower()
            source_url = row.get("source_url", "").strip()
            source_type = row.get("source_type", "manual_research").strip()
            observed_at = row.get("observed_at", "").strip() or None
            notes = row.get("notes", "").strip()
            cur = conn.execute(
                "INSERT OR IGNORE INTO enrichment_facts(venue_id,field_name,field_value,confidence,source_url,source_type,observed_at,verified_at,notes) VALUES(?,?,?,?,?,?,?,?,?)",
                (venue_id, field_name, field_value, confidence, source_url, source_type, observed_at, now(), notes),
            )
            written += max(cur.rowcount, 0)
    conn.commit()
    return seen, written
