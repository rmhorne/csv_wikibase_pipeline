# CSV to Wikibase Pipeline Assessment

## Overview

This repository contains a small CSV → Wikibase ingest pipeline. Its main intention is to:

- read CSV rows,
- build an ingest plan of Wikibase-style statements,
- resolve or generate local QID mappings for works and entities,
- write the plan to JSON,
- optionally simulate Wikibase entity lookups.

The pipeline is not a full transactional import system; it is a lightweight planning and resolution helper.

---

## Key files and responsibilities

### `run.py`

- User-facing CLI entrypoint.
- Accepts `--file` and `--mode`.
- Calls `ingest.run()`.

### `ingest.py`

- Orchestrates the pipeline.
- Reads the CSV with `pandas`.
- Loads configuration from `config.json`.
- Loads the cache from `cache.json`.
- Builds the statement plan row-by-row via `generate_plan()`.
- Saves updated cache.
- Chooses the executor for `dry`, `simulate`, or `commit`.

### `triples.py`

- Converts one CSV row into a list of `Statement` objects.
- Uses the configured `work_key` from `config.json` to identify a work.
- Maps CSV columns to properties based on:
  - `entity_properties`
  - `literal_properties`
  - `flags`
  - `languages`
- Handles institution name/type as a special case.

### `resolver.py`

- Provides local QID resolution and creation.
- `resolve_work()` creates/reuses work IDs under `cache["works"]`.
- `resolve_or_create()` creates/reuses entity IDs under `cache["entities"]`.
- `resolve_institution()` currently delegates to generic entity resolution.

### `cache.py`

- Reads and writes `cache.json`.
- Preserves entity and work ID mappings across runs.

### `utils.py`

- Shared helpers for JSON file loading/writing and text normalization.
- Centralizes path definitions for `cache.json`, `config.json`, and `connection.json`.

### `output.py`

- Writes JSON output for:
  - `plan_output.json`
  - `resolution_output.json`
  - `missing_entities.json`
  - `entity_seed_plan.json`

### `executors/`

- `dry.py`
  - Writes the ingest plan JSON without talking to Wikibase.
- `simulate.py`
  - Performs Wikibase entity searches.
  - Writes resolution and missing entity outputs.
- `commit.py`
  - Not implemented yet.

### `wikibase_search.py`

- Handles Wikibase API connection and authentication.
- Uses `wbsearchentities` to lookup labels.
- Returns both raw and exact filtered matches.

### `config.json`

- Defines how CSV columns are mapped to Wikibase properties.
- Includes `work_key`, `entity_properties`, `literal_properties`, `flags`, and `languages`.

### `connection.example.json`

- Example Wikibase connection configuration.
- Should be copied to `connection.json` for simulate mode.

---

## Operational intent

### Dry mode

- Generates `plan_output.json`.
- Useful for validating mapping and plan structure without network access.

### Simulate mode

- Queries Wikibase for entity labels.
- Generates:
  - `resolution_output.json`
  - `missing_entities.json`
  - `entity_seed_plan.json`
- Requires a real `connection.json` and network access.

### Commit mode

- Present but not implemented.
- Would be the place to add actual Wikibase writing behavior.

---

## Usage

```bash
python3 run.py --file /path/to/data.csv --mode dry
```

To check entity resolution with a Wikibase endpoint:

```bash
python3 run.py --file /path/to/data.csv --mode simulate
```

---

## Notes on current design

- The pipeline is intentionally lightweight.
- It uses local cache-generated QIDs, not real Wikibase QIDs.
- `simulate` is the only mode that interacts with Wikibase.
- `commit` is a placeholder for future implementation.

## Possible improvements

- Implement `commit` mode if actual write support is needed.
- Add better validation for `config.json`.
- Add tests for plan generation and executor behavior.
- Consider moving `executors` into a single module if the pipeline remains small.
- Improve error handling around file loading and Wikibase requests.
