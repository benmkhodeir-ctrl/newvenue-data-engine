from __future__ import annotations

import sqlite3
from pathlib import Path


def connect(path: str | Path) -> sqlite3.Connection:
    db_path = Path(path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialise(conn: sqlite3.Connection) -> None:
    statements = (
        "CREATE TABLE IF NOT EXISTS pipeline_runs (id INTEGER PRIMARY KEY AUTOINCREMENT, run_type TEXT NOT NULL, started_at TEXT NOT NULL, completed_at TEXT, status TEXT NOT NULL DEFAULT 'running', source_file TEXT, records_seen INTEGER NOT NULL DEFAULT 0, records_written INTEGER NOT NULL DEFAULT 0, notes TEXT)",
        "CREATE TABLE IF NOT EXISTS source_records (id INTEGER PRIMARY KEY AUTOINCREMENT, source_system TEXT NOT NULL, external_id TEXT NOT NULL, source_url TEXT, fetched_at TEXT NOT NULL, effective_date TEXT, record_type TEXT, raw_json TEXT NOT NULL, record_hash TEXT NOT NULL, UNIQUE(source_system, external_id, record_hash))",
        "CREATE TABLE IF NOT EXISTS venues (id INTEGER PRIMARY KEY AUTOINCREMENT, canonical_name TEXT, address_line TEXT, suburb TEXT, postcode TEXT, state TEXT NOT NULL DEFAULT 'NSW', lga TEXT, normalised_address TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)",
        "CREATE TABLE IF NOT EXISTS signals (id INTEGER PRIMARY KEY AUTOINCREMENT, venue_id INTEGER, source_record_id INTEGER NOT NULL, signal_type TEXT NOT NULL, signal_date TEXT, application_type TEXT, status TEXT, description TEXT, opportunity_class TEXT, opportunity_score INTEGER, classification_confidence REAL, classification_reason TEXT, created_at TEXT NOT NULL)",
        "CREATE TABLE IF NOT EXISTS signal_matches (id INTEGER PRIMARY KEY AUTOINCREMENT, left_signal_id INTEGER NOT NULL, right_signal_id INTEGER NOT NULL, match_type TEXT NOT NULL, match_score REAL NOT NULL, match_reason TEXT, created_at TEXT NOT NULL, UNIQUE(left_signal_id, right_signal_id))",
        "CREATE TABLE IF NOT EXISTS enrichment_facts (id INTEGER PRIMARY KEY AUTOINCREMENT, venue_id INTEGER NOT NULL, field_name TEXT NOT NULL, field_value TEXT NOT NULL, confidence TEXT NOT NULL, source_url TEXT, source_type TEXT, observed_at TEXT, verified_at TEXT NOT NULL, notes TEXT, UNIQUE(venue_id, field_name, field_value, source_url))",
        "CREATE TABLE IF NOT EXISTS enrichment_queue (id INTEGER PRIMARY KEY AUTOINCREMENT, venue_id INTEGER NOT NULL, task_type TEXT NOT NULL, priority INTEGER NOT NULL DEFAULT 50, status TEXT NOT NULL DEFAULT 'pending', created_at TEXT NOT NULL, completed_at TEXT, notes TEXT, UNIQUE(venue_id, task_type))",
    )
    for statement in statements:
        conn.execute(statement)
    conn.commit()
