from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .classify import classify_text
from .normalise import clean_text, first, normalise_address, parse_date


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def record_hash(payload: dict) -> str:
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _start_run(conn, run_type: str, source_file: str) -> int:
    cur = conn.execute(
        "INSERT INTO pipeline_runs(run_type, started_at, status, source_file) VALUES(?,?,?,?)",
        (run_type, now(), "running", source_file),
    )
    return cur.lastrowid


def _finish_run(conn, run_id: int, seen: int, written: int, notes: str = "") -> None:
    conn.execute(
        "UPDATE pipeline_runs SET completed_at=?, status='completed', records_seen=?, records_written=?, notes=? WHERE id=?",
        (now(), seen, written, notes, run_id),
    )
    conn.commit()


def _upsert_venue(conn, name: str, address: str, suburb: str, postcode: str, lga: str) -> int | None:
    location_text = " ".join(part for part in (address, suburb, postcode) if part)
    norm = normalise_address(location_text)
    if not norm:
        return None
    existing = conn.execute(
        "SELECT id FROM venues WHERE normalised_address=? ORDER BY id LIMIT 1", (norm,)
    ).fetchone()
    if existing:
        conn.execute(
            "UPDATE venues SET canonical_name=COALESCE(NULLIF(?,''),canonical_name), suburb=COALESCE(NULLIF(?,''),suburb), postcode=COALESCE(NULLIF(?,''),postcode), lga=COALESCE(NULLIF(?,''),lga), updated_at=? WHERE id=?",
            (name, suburb, postcode, lga, now(), existing["id"]),
        )
        return int(existing["id"])
    cur = conn.execute(
        "INSERT INTO venues(canonical_name,address_line,suburb,postcode,lga,normalised_address,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)",
        (name, address, suburb, postcode, lga, norm, now(), now()),
    )
    return int(cur.lastrowid)


def ingest_liquor_csv(conn, path: str | Path) -> tuple[int, int]:
    path = Path(path)
    run_id = _start_run(conn, "ingest_liquor_csv", str(path))
    seen = written = 0
    with path.open(newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            seen += 1
            app_no = first(row, "application_number", "application number", "application no", "application") or f"row-{seen}"
            app_type = first(row, "application_type", "application type", "type")
            name = first(row, "licence_name", "licence name", "venue_name", "venue", "proposed licence name")
            address = first(row, "address", "premises_address", "premises address", "location")
            suburb = first(row, "suburb")
            postcode = first(row, "postcode", "post code")
            lga = first(row, "lga", "local government area")
            posted = parse_date(first(row, "posted_date", "posted date", "date posted", "lodged date", "date"))
            status = first(row, "status", "application status")
            source_url = first(row, "source_url", "source url", "url")
            description = first(row, "description", "notes", "details")
            source_system = first(row, "source_system", "source system") or "nsw_liquor_noticeboard"

            payload = {k: clean_text(v) for k, v in row.items()}
            rh = record_hash(payload)
            cur = conn.execute(
                "INSERT OR IGNORE INTO source_records(source_system,external_id,source_url,fetched_at,effective_date,record_type,raw_json,record_hash) VALUES(?,?,?,?,?,?,?,?)",
                (source_system, app_no, source_url, now(), posted, app_type, json.dumps(payload, ensure_ascii=False), rh),
            )
            if cur.rowcount == 0:
                continue
            source_id = int(cur.lastrowid)
            venue_id = _upsert_venue(conn, name, address, suburb, postcode, lga)
            c = classify_text(app_type, description, status)
            conn.execute(
                "INSERT INTO signals(venue_id,source_record_id,signal_type,signal_date,application_type,status,description,opportunity_class,opportunity_score,classification_confidence,classification_reason,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (venue_id, source_id, "liquor_application", posted, app_type, status, description, c.opportunity_class, c.score, c.confidence, c.reason, now()),
            )
            written += 1
    _finish_run(conn, run_id, seen, written)
    return seen, written


def ingest_da_csv(conn, path: str | Path) -> tuple[int, int]:
    path = Path(path)
    run_id = _start_run(conn, "ingest_da_csv", str(path))
    seen = written = 0
    with path.open(newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            seen += 1
            app_no = first(row, "application_number", "application number", "application no", "da number", "planning portal application number") or f"row-{seen}"
            description = first(row, "description", "development description", "proposal", "development type")
            address = first(row, "address", "property address", "site address", "location")
            suburb = first(row, "suburb")
            postcode = first(row, "postcode", "post code")
            lga = first(row, "lga", "council", "local government area")
            lodged = parse_date(first(row, "lodgement_date", "lodgement date", "date lodged", "application date", "date"))
            status = first(row, "status", "application status")
            source_url = first(row, "source_url", "source url", "url")
            source_system = first(row, "source_system", "source system") or "nsw_planning_portal"

            payload = {k: clean_text(v) for k, v in row.items()}
            rh = record_hash(payload)
            cur = conn.execute(
                "INSERT OR IGNORE INTO source_records(source_system,external_id,source_url,fetched_at,effective_date,record_type,raw_json,record_hash) VALUES(?,?,?,?,?,?,?,?)",
                (source_system, app_no, source_url, now(), lodged, "development_application", json.dumps(payload, ensure_ascii=False), rh),
            )
            if cur.rowcount == 0:
                continue
            source_id = int(cur.lastrowid)
            venue_id = _upsert_venue(conn, "", address, suburb, postcode, lga)
            c = classify_text("development application", description, status)
            conn.execute(
                "INSERT INTO signals(venue_id,source_record_id,signal_type,signal_date,application_type,status,description,opportunity_class,opportunity_score,classification_confidence,classification_reason,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (venue_id, source_id, "development_application", lodged, "development application", status, description, c.opportunity_class, c.score, c.confidence, c.reason, now()),
            )
            written += 1
    _finish_run(conn, run_id, seen, written)
    return seen, written
