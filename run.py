import pandas as pd
from cache import load_cache, save_cache
from triples import build_plan


CSV_PATH = "data/raw/milken_spotify.csv"
CACHE_PATH = "out/cache.json"


def is_valid_row(row):
    def ok(v):
        if v is None:
            return False
        v = str(v).strip().lower()
        return v not in {"", "nan", "none", "null"}

    return any([
        ok(row.get("Title")),
        ok(row.get("Composer")),
        ok(row.get("Spotify Album")),
        ok(row.get("Album")),
    ])


def run():
    df = pd.read_csv(CSV_PATH)
    cache = load_cache(CACHE_PATH)

    plan = []

    for i, (_, row) in enumerate(df.iterrows()):

        # HARD GATE: prevent empty entity pollution
        if not is_valid_row(row):
            print(f"[ROW SKIP] {i} completely empty or invalid")
            continue

        statements, cache = build_plan(
            row=row,
            config=None,
            cache=cache,
            row_index=i
        )

        plan.extend(statements)

    save_cache(cache, CACHE_PATH)
    return plan


if __name__ == "__main__":
    plan = run()

    for s in plan[:20]:
        print({
            "subject": s.subject,
            "predicate": s.predicate,
            "object": s.object,
            "label": s.object_label
        })

    print("\nTOTAL:", len(plan))