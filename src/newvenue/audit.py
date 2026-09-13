from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


def export_audit(conn, out_dir: str | Path) -> dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    venues = conn.execute(
        """
        SELECT v.*, MAX(s.opportunity_score) AS max_score,
               GROUP_CONCAT(DISTINCT s.signal_type) AS signal_types,
               GROUP_CONCAT(DISTINCT s.opportunity_class) AS opportunity_classes
        FROM venues v
        LEFT JOIN signals s ON s.venue_id=v.id
        GROUP BY v.id
        ORDER BY max_score DESC, v.id
        """
    ).fetchall()

    fact_rows = conn.execute(
        "SELECT venue_id,field_name,field_value,confidence,source_url FROM enrichment_facts"
    ).fetchall()
    facts: dict[int, dict[str, list]] = {}
    fields: set[str] = set()
    for fact in fact_rows:
        fields.add(fact["field_name"])
        facts.setdefault(int(fact["venue_id"]), {}).setdefault(fact["field_name"], []).append(dict(fact))
    ordered_fields = sorted(fields)

    audit_path = out_dir / "enrichment_audit.csv"
    with audit_path.open("w", newline="", encoding="utf-8") as fh:
        columns = [
            "venue_id",
            "canonical_name",
            "address_line",
            "suburb",
            "postcode",
            "max_score",
            "signal_types",
            "opportunity_classes",
        ]
        for field in ordered_fields:
            columns += [f"{field}_present", f"{field}_confidence"]
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        for venue in venues:
            row = {
                "venue_id": venue["id"],
                "canonical_name": venue["canonical_name"],
                "address_line": venue["address_line"],
                "suburb": venue["suburb"],
                "postcode": venue["postcode"],
                "max_score": venue["max_score"],
                "signal_types": venue["signal_types"],
                "opportunity_classes": venue["opportunity_classes"],
            }
            venue_facts = facts.get(int(venue["id"]), {})
            for field in ordered_fields:
                entries = venue_facts.get(field, [])
                row[f"{field}_present"] = "yes" if entries else "no"
                row[f"{field}_confidence"] = entries[0]["confidence"] if entries else ""
            writer.writerow(row)

    total = len(venues)
    coverage = {}
    for field in ordered_fields:
        present = sum(1 for venue in venues if facts.get(int(venue["id"]), {}).get(field))
        coverage[field] = {
            "present": present,
            "total": total,
            "coverage_pct": round((present / total * 100) if total else 0, 1),
        }

    class_counts = Counter()
    for row in conn.execute("SELECT opportunity_class, COUNT(*) n FROM signals GROUP BY opportunity_class"):
        class_counts[row["opportunity_class"]] = row["n"]

    summary = {
        "venues": total,
        "signals": conn.execute("SELECT COUNT(*) n FROM signals").fetchone()["n"],
        "matches": conn.execute("SELECT COUNT(*) n FROM signal_matches").fetchone()["n"],
        "enrichment_facts": len(fact_rows),
        "classification_counts": dict(class_counts),
        "coverage": coverage,
        "outputs": {"audit_csv": str(audit_path)},
    }
    summary_path = out_dir / "audit_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    summary["outputs"]["summary_json"] = str(summary_path)
    return summary
