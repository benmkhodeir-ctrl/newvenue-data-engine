from __future__ import annotations

import json
from datetime import datetime, timezone

from .operator_resolver import Evidence, resolve_operator


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_venue_operator(conn, venue_id: int, *, address: str, tenancy: str = "", venue_name: str = ""):
    rows = conn.execute(
        """SELECT operator_name, source_url, source_type, address, tenancy, venue_name,
                  evidence_text, named_person, public_contact
           FROM operator_evidence WHERE venue_id=?""",
        (venue_id,),
    ).fetchall()
    evidence = [Evidence(**dict(row)) for row in rows]
    result = resolve_operator(evidence, address=address, tenancy=tenancy, venue_name=venue_name)
    conn.execute(
        """INSERT INTO operator_resolutions
           (venue_id, operator_name, score, confidence, reasons_json, source_urls_json,
            named_person, public_contact, resolved_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(venue_id) DO UPDATE SET
             operator_name=excluded.operator_name,
             score=excluded.score,
             confidence=excluded.confidence,
             reasons_json=excluded.reasons_json,
             source_urls_json=excluded.source_urls_json,
             named_person=excluded.named_person,
             public_contact=excluded.public_contact,
             resolved_at=excluded.resolved_at""",
        (
            venue_id,
            result.operator_name,
            result.score,
            result.confidence,
            json.dumps(result.reasons),
            json.dumps(result.source_urls),
            result.named_person,
            result.public_contact,
            now(),
        ),
    )
    conn.commit()
    return result
