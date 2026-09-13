from __future__ import annotations

from datetime import datetime, timezone


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def match_same_venue_signals(conn) -> int:
    rows = conn.execute(
        "SELECT s1.id AS left_id, s2.id AS right_id, v.normalised_address FROM signals s1 JOIN signals s2 ON s1.venue_id=s2.venue_id AND s1.id < s2.id JOIN venues v ON v.id=s1.venue_id WHERE s1.signal_type <> s2.signal_type"
    ).fetchall()
    written = 0
    for row in rows:
        reason = f"Signals share normalised venue address: {row['normalised_address']}"
        cur = conn.execute(
            "INSERT OR IGNORE INTO signal_matches(left_signal_id,right_signal_id,match_type,match_score,match_reason,created_at) VALUES(?,?,?,?,?,?)",
            (row["left_id"], row["right_id"], "same_normalised_address", 1.0, reason, now()),
        )
        written += max(cur.rowcount, 0)
    conn.commit()
    return written
