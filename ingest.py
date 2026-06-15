# ingest.py

import csv
from utils import load_json


def load(csv_path, config_path, cache_path):
    """
    PURE LOADER
    - no interpretation
    - no defaults for semantics
    """

    print("\n[INGEST] Loading config...")

    config = load_json(config_path)
    if config is None:
        raise RuntimeError("Config failed to load")

    print("[INGEST] Config loaded")

    print("\n[INGEST] Loading CSV...")

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    print(f"[INGEST] Rows loaded: {len(rows)}")

    print("\n[INGEST] Loading cache...")

    try:
        cache = load_json(cache_path)
        if cache is None:
            cache = {}
        print("[INGEST] Cache loaded")
    except Exception:
        cache = {}
        print("[INGEST] Cache not found, starting empty")

    return config, rows, cache