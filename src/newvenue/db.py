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


def migrate(conn: sqlite3.Connection, migrations_dir: str | Path = "migrations") -> None:
    schema_path = Path(migrations_dir) / "001_initial.sql"
    conn.executescript(schema_path.read_text(encoding="utf-8"))
    conn.commit()
