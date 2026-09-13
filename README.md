# NewVenue Data Engine — V0

Validation-stage pipeline for building a structured dataset of upcoming NSW hospitality venues from public commercial signals.

**This repository is intentionally not a web product.** It exists to prove the collection, matching, classification and enrichment process before any customer-facing product is built.

## What works now

- SQLite schema/migrations
- CSV ingestion for Liquor & Gaming-style application data
- CSV ingestion for NSW Planning/DA-style data
- raw-record preservation and deduplication
- address normalisation
- deterministic opportunity classification
- same-address cross-source matching
- enrichment task queue
- manual/semi-automated enrichment fact import with provenance/confidence
- enrichment coverage audit CSV + JSON
- synthetic end-to-end fixtures/tests

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
newvenue init
newvenue run-fixtures
```

Outputs are written under `data/out/`.

## Design rule

A blank value is better than a confidently wrong value. Every enrichment fact stores its confidence and provenance.

See `00 — Data Engine Source of Truth.md` for current scope and architecture decisions.
