CREATE TABLE IF NOT EXISTS operator_evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venue_id INTEGER NOT NULL,
    operator_name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    source_type TEXT NOT NULL,
    address TEXT,
    tenancy TEXT,
    venue_name TEXT,
    evidence_text TEXT,
    named_person TEXT,
    public_contact TEXT,
    observed_at TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(venue_id, operator_name, source_url),
    FOREIGN KEY (venue_id) REFERENCES venues(id)
);

CREATE INDEX IF NOT EXISTS idx_operator_evidence_venue
    ON operator_evidence(venue_id);

CREATE TABLE IF NOT EXISTS operator_resolutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venue_id INTEGER NOT NULL UNIQUE,
    operator_name TEXT,
    score INTEGER NOT NULL DEFAULT 0,
    confidence TEXT NOT NULL CHECK(confidence IN ('confirmed','strong','probable','unknown')),
    reasons_json TEXT NOT NULL,
    source_urls_json TEXT NOT NULL,
    named_person TEXT,
    public_contact TEXT,
    resolved_at TEXT NOT NULL,
    FOREIGN KEY (venue_id) REFERENCES venues(id)
);
