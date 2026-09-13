# 00 — Data Engine Source of Truth

Last updated: 13/09/2026

## Purpose

Build and validate a repeatable NSW hospitality-opening intelligence process and structured dataset. This stage is **not** a customer-facing product build.

The business hypothesis to test later is that hospitality suppliers may pay for early, qualified intelligence about new venues. The current engineering hypothesis is narrower: public commercial signals can be collected, matched, enriched and classified with sufficient accuracy and coverage to create a reliable dataset.

## Authority order

1. Ben's explicit current instruction or correction.
2. Confirmed live source evidence and current primary-source documentation.
3. This source-of-truth file.
4. Repository code/tests.
5. Historical planning notes and hypotheses.

## Current scope

### Build now

- source-controlled data model;
- raw-source preservation;
- liquor application import adapter;
- planning/DA import adapter;
- address normalisation and cross-source matching;
- deterministic first-pass opportunity classification;
- enrichment task queue and fact/provenance model;
- enrichment audit outputs;
- synthetic fixtures and automated tests.

### Validate next

- supported automated ingestion method for Liquor & Gaming NSW Noticeboard;
- real NSW Planning Portal DA feed/export mapping;
- 30–50 current hospitality venue records;
- free/manual enrichment coverage and accuracy;
- opening-stage inference and timing;
- automation rate and human-review burden.

### Explicitly not building yet

- website;
- domain;
- customer dashboard;
- mobile app;
- subscriptions/billing;
- CRM integration;
- automated marketing;
- paid contact-enrichment service;
- Australia-wide ingestion;
- supplier prospecting product features.

## Architecture decision

The previous Web Product Builder process is retained as the operating discipline, but the Cloudflare-first product architecture is intentionally deferred.

V0 is a Python + SQLite ETL/data-quality repository because the business assumption is about the dataset, not a web interface. Once the collection/enrichment process is stable, the pipeline can be moved to scheduled Workers/D1 or another low-maintenance runtime without changing the conceptual entities.

## Data model

- `source_records`: immutable/raw snapshots with source system, external identifier, URL and hash.
- `venues`: canonical place/address records.
- `signals`: liquor, planning and later other commercial signals associated with venues.
- `signal_matches`: evidence that signals from different sources refer to the same opportunity.
- `entities`: operators/companies/other organisations.
- `venue_entities`: operator/owner/group relationships with confidence/provenance.
- `enrichment_facts`: field-level facts with confidence and source URL.
- `enrichment_queue`: work still required to enrich candidate venues.
- `pipeline_runs`: reproducibility/audit history.

## Classification principles

The system must not use an LLM as a fact oracle. Deterministic rules remove obvious low-value records first. AI can later assist with ambiguous interpretation, but every material fact must retain provenance and confidence.

Confidence levels are: `confirmed`, `strong`, `probable`, `unknown`. Unknown values remain blank.

## V0 success criterion

Create a real 30–50 venue NSW sample where each record has explicit source provenance, opportunity classification, enrichment coverage/confidence and a measurable human-review burden. Only then define the customer product and price.
