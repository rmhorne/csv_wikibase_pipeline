import pandas as pd
from utils import load_json
from cache import load_cache, save_cache
from triples import build_plan


def run(csv_path, config_path, cache_path):
    df = pd.read_csv(csv_path)
    config = load_json(config_path)

    cache = load_cache(cache_path)

    plan = []

    for _, row in df.iterrows():
        statements, cache = build_plan(row, config, cache)
        plan.extend(statements)

    save_cache(cache, cache_path)

    return plan