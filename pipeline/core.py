import json
import csv
import sys


# =========================================================
# LOADERS
# =========================================================

def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_csv(path):
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


# =========================================================
# REFERENCES
# =========================================================

def build_references(config):
    source = config.get("source", {})

    return {
        "default_source_qid": source.get("qid"),
        "default_source_label": source.get("label"),
        "id_prefix": source.get("id_prefix", "QW")
    }


# =========================================================
# ENTITY RESOLUTION CORE
# =========================================================

def normalize_entity(value):
    if value is None:
        return ""
    return str(value).strip().lower()


def create_entity(label, cache, references):
    prefix = references["id_prefix"]

    cache["counter"] += 1
    entity_id = f"{prefix}{cache['counter']}"

    entity_obj = {
        "id": entity_id,
        "label": label
    }

    cache["entities"][label] = entity_obj

    return entity_obj


def resolve_entity(value, cache, references):
    key = normalize_entity(value)

    if key in cache["entities"]:
        return cache["entities"][key]

    return create_entity(key, cache, references)


# =========================================================
# ROW PROCESSING CORE
# =========================================================

def process_single_row(row, config, cache, plan, references, row_index):
    title = row.get("Title")
    composer = row.get("Composer")

    title_entity = resolve_entity(title, cache, references)
    composer_entity = resolve_entity(composer, cache, references)

    row_plan = {
        "row_index": row_index,
        "raw": row,
        "resolved_entities": {
            "title": title_entity,
            "composer": composer_entity
        },
        "triples": []
    }   

    plan["rows"].append(row_plan)


def process_rows(rows, config, cache, plan, references):
    for i, row in enumerate(rows):
        process_single_row(row, config, cache, plan, references, i)


# =========================================================
# IO HELPERS (EXPORT)
# =========================================================

def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# =========================================================
# MAIN
# =========================================================

def main():
    config_path = "../config/config-v3.json"
    csv_path = "../data/raw/milken_spotify.csv"

    config = load_config(config_path)
    rows = load_csv(csv_path)

    cache = {
        "entities": {},
        "counter": 0
    }

    plan = {
        "rows": []
    }

    references = build_references(config)

    print("CONFIG LOADED")
    print(json.dumps(config, indent=2))

    print("\nCSV LOADED")
    print(f"Rows: {len(rows)}")

    process_rows(rows, config, cache, plan, references)

    # =========================================================
    # EXPORT OUTPUTS
    # =========================================================

    write_json("cache.json", cache)
    write_json("plan.json", plan)

    print("\nDONE")
    print(f"Processed rows: {len(plan['rows'])}")
    print("Wrote: cache.json")
    print("Wrote: plan.json")


if __name__ == "__main__":
    main()