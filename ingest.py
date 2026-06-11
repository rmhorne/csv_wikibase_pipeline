import pandas as pd
from utils import load_json
from cache import load_cache, save_cache
from triples import build_plan


def run(csv_path, config_path, cache_path):
    df = pd.read_csv(csv_path)
    config = load_json(config_path)

    cache = load_cache(cache_path)

    plan = []

    # IMPORTANT: stable row indexing for provenance
    for row_index, (_, row) in enumerate(df.iterrows()):
        statements, cache = build_plan(
            row=row,
            config=config,
            cache=cache,
            row_index=row_index
        )

        plan.extend(statements)

    save_cache(cache, cache_path)

    return plan