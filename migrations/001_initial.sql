PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS pipeline_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_type TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    status TEXT NOT NULL DEFAULT 'running',
    source_file TEXT,
    records_seen INTEGER NOT NULL DEFAULT 0,
    records_written INTEGER NOT NULL DEFAULT 0,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS source_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_system TEXT NOT NULL,
    external_id TEXT NOT NULL,
    source_url TEXT,
    fetched_at TEXT NOT NULL,
    effective_date TEXT,
    record_type TEXT,
    raw_json TEXT NOT NULL,
    record_hash TEXT NOT NULL,
    UNIQUE(source_system, external_id, record_hash)
);
CREATE INDEX IF NOT EXISTS idx_source_records_system_external
    ON source_records(source_system, external_id);

CREATE TABLE IF NOT EXISTS venues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    canonical_name TEXT,
    address_line TEXT,
    suburb TEXT,
    postcode TEXT,
    state TEXT NOT NULL DEFAULT 'NSW',
    lga TEXT,
    normalised_address TEXT,
    latitude REAL,
    longitude REAL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_venues_normalised_address ON venues(normalised_address);

CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venue_id INTEGER,
    source_record_id INTEGER NOT NULL,
    signal_type TEXT NOT NULL,
    signal_date TEXT,
    application_type TEXT,
    status TEXT,
    description TEXT,
    opportunity_class TEXT,
    opportunity_score INTEGER,
    classification_confidence REAL,
    classification_reason TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (venue_id) REFERENCES venues(id),
    FOREIGN KEY (source_record_id) REFERENCES source_records(id)
);
CREATE INDEX IF NOT EXISTS idx_signals_venue ON signals(venue_id);
CREATE INDEX IF NOT EXISTS idx_signals_class ON signals(opportunity_class);

CREATE TABLE IF NOT EXISTS signal_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    left_signal_id INTEGER NOT NULL,
    right_signal_id INTEGER NOT NULL,
    match_type TEXT NOT NULL,
    match_score REAL NOT NULL,
    match_reason TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(left_signal_id, right_signal_id),
    FOREIGN KEY (left_signal_id) REFERENCES signals(id),
    FOREIGN KEY (right_signal_id) REFERENCES signals(id)
);

CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,
    legal_name TEXT,
    trading_name TEXT,
    abn TEXT,
    acn TEXT,
    website TEXT,
    phone TEXT,
    email TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_entities_abn ON entities(abn);
CREATE INDEX IF NOT EXISTS idx_entities_acn ON entities(acn);

CREATE TABLE IF NOT EXISTS venue_entities (
    venue_id INTEGER NOT NULL,
    entity_id INTEGER NOT NULL,
    relationship_type TEXT NOT NULL,
    confidence REAL NOT NULL,
    source_url TEXT,
    notes TEXT,
    PRIMARY KEY (venue_id, entity_id, relationship_type),
    FOREIGN KEY (venue_id) REFERENCES venues(id),
    FOREIGN KEY (entity_id) REFERENCES entities(id)
);

CREATE TABLE IF NOT EXISTS enrichment_facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venue_id INTEGER NOT NULL,
    field_name TEXT NOT NULL,
    field_value TEXT NOT NULL,
    confidence TEXT NOT NULL CHECK(confidence IN ('confirmed','strong','probable','unknown')),
    source_url TEXT,
    source_type TEXT,
    observed_at TEXT,
    verified_at TEXT NOT NULL,
    notes TEXT,
    UNIQUE(venue_id, field_name, field_value, source_url),
    FOREIGN KEY (venue_id) REFERENCES venues(id)
);
CREATE INDEX IF NOT EXISTS idx_enrichment_venue_field ON enrichment_facts(venue_id, field_name);

CREATE TABLE IF NOT EXISTS enrichment_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venue_id INTEGER NOT NULL,
    task_type TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 50,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL,
    completed_at TEXT,
    notes TEXT,
    UNIQUE(venue_id, task_type),
    FOREIGN KEY (venue_id) REFERENCES venues(id)
);
