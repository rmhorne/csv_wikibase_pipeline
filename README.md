# CSV to Wikibase Pipeline

This directory contains a standalone CSV → Wikibase ingest pipeline.

## Usage

From the `code/csv_wikibase_pipeline` directory:

```bash
python3 run.py --file /path/to/milken_base.csv --mode dry
```

Modes:
- `dry`: generate `plan_output.json` only
- `simulate`: search Wikibase for entity labels and generate `resolution_output.json`, `missing_entities.json`, and `entity_seed_plan.json`
- `commit`: not implemented yet

## Required files

- `config.json` — ingest mapping and field-to-property configuration
- `connection.json` — Wikibase API connection settings.
  - Copy `connection.example.json` and update it with your environment.

## Outputs

- `plan_output.json` — tuple plan list generated from the CSV
- `cache.json` — cached work/entity IDs between runs
- `resolution_output.json`, `missing_entities.json`, `entity_seed_plan.json` — generated in `simulate` mode

## Notes

- `dry` mode works without a Wikibase connection.
- `simulate` mode requires a valid `connection.json`.
- The pipeline is intentionally lightweight and separate from `code/milken_ingest`.
