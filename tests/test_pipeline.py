from pathlib import Path

from newvenue.audit import export_audit
from newvenue.db import connect, migrate
from newvenue.enrichment import ingest_enrichment_csv, queue_candidates
from newvenue.ingest import ingest_da_csv, ingest_liquor_csv
from newvenue.match import match_same_venue_signals


def test_fixture_pipeline(tmp_path):
    root = Path(__file__).resolve().parents[1]
    conn = connect(tmp_path / "test.db")
    migrate(conn, root / "migrations")
    ingest_liquor_csv(conn, root / "fixtures" / "liquor_sample.csv")
    ingest_da_csv(conn, root / "fixtures" / "da_sample.csv")
    assert match_same_venue_signals(conn) >= 2
    assert queue_candidates(conn) > 0
    ingest_enrichment_csv(conn, root / "fixtures" / "enrichment_sample.csv")
    summary = export_audit(conn, tmp_path / "out")
    assert summary["venues"] == 3
    assert summary["signals"] == 6
