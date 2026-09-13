from __future__ import annotations

import argparse
import json
from pathlib import Path

from .audit import export_audit
from .db import connect, migrate
from .enrichment import ingest_enrichment_csv, queue_candidates
from .ingest import ingest_da_csv, ingest_liquor_csv
from .match import match_same_venue_signals


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="newvenue", description="NewVenue validation-stage data engine")
    parser.add_argument("--db", default="data/newvenue.db", help="SQLite database path")
    parser.add_argument("--migrations", default="migrations", help="Migrations directory")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    cmd = sub.add_parser("ingest-liquor")
    cmd.add_argument("csv")
    cmd = sub.add_parser("ingest-da")
    cmd.add_argument("csv")
    sub.add_parser("match")
    cmd = sub.add_parser("queue-enrichment")
    cmd.add_argument("--minimum-score", type=int, default=55)
    cmd = sub.add_parser("ingest-enrichment")
    cmd.add_argument("csv")
    cmd = sub.add_parser("audit")
    cmd.add_argument("--out", default="data/out")
    sub.add_parser("run-fixtures")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    conn = connect(args.db)
    migrate(conn, args.migrations)

    if args.command == "init":
        print(f"Initialised {args.db}")
    elif args.command == "ingest-liquor":
        print(dict(zip(("seen", "written"), ingest_liquor_csv(conn, args.csv))))
    elif args.command == "ingest-da":
        print(dict(zip(("seen", "written"), ingest_da_csv(conn, args.csv))))
    elif args.command == "match":
        print({"matches_written": match_same_venue_signals(conn)})
    elif args.command == "queue-enrichment":
        print({"tasks_queued": queue_candidates(conn, args.minimum_score)})
    elif args.command == "ingest-enrichment":
        print(dict(zip(("seen", "written"), ingest_enrichment_csv(conn, args.csv))))
    elif args.command == "audit":
        print(json.dumps(export_audit(conn, args.out), indent=2))
    elif args.command == "run-fixtures":
        base = Path("fixtures")
        ingest_liquor_csv(conn, base / "liquor_sample.csv")
        ingest_da_csv(conn, base / "da_sample.csv")
        match_same_venue_signals(conn)
        queue_candidates(conn)
        ingest_enrichment_csv(conn, base / "enrichment_sample.csv")
        print(json.dumps(export_audit(conn, "data/out"), indent=2))

    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
