import pandas as pd

from cache import load_cache, save_cache
from triples import generate_plan
from executors.commit import CommitExecutor
from executors.dry import DryExecutor
from executors.simulate import SimulateExecutor
from utils import load_json_file


EXECUTORS = {
    "dry": DryExecutor,
    "simulate": SimulateExecutor,
    "commit": CommitExecutor,
}


def validate_config(config):
    predicate_types = {}

    for field_name, spec in config["fields"].items():

        predicate = spec["predicate"]
        field_type = spec["type"]

        if predicate not in predicate_types:
            predicate_types[predicate] = field_type
            continue

        if predicate_types[predicate] != field_type:
            raise ValueError(
                f"CONFIG ERROR: {predicate} conflict at {field_name}"
            )


def _dedupe_key(stmt):
    return (
        stmt.subject,
        stmt.predicate,
        stmt.object,
        stmt.object_type
    )


def run(file_path, config_path, mode="dry"):
    df = pd.read_csv(file_path)
    config = load_json_file(config_path)

    validate_config(config)

    cache = load_cache()

    # HARD GUARD (CRITICAL FIX)
    if not isinstance(cache, dict):
        raise TypeError(f"[FATAL] cache must be dict at start, got {type(cache)}")

    # -----------------------------
    # FRBR MEMORY LAYERS
    # -----------------------------
    cache.setdefault("entities_by_type", {})
    cache.setdefault("expressions", {})
    cache.setdefault("frbr_nodes", {})

    plan_all = []
    seen = set()

    total = len(df)

    for i, row in df.iterrows():

        # HARD GUARD PER ITERATION (THIS IS THE FIX THAT STOPS SILENT DRIFT)
        if not isinstance(cache, dict):
            raise TypeError(f"[CACHE CORRUPTION DETECTED at row {i}] got {type(cache)}")

        result = generate_plan(row, config, cache)

        # strict unpack validation
        if not isinstance(result, tuple) or len(result) != 2:
            raise TypeError(
                f"[generate_plan contract violation] expected (plan, cache), got {type(result)}"
            )

        plan, cache = result

        # SECOND GUARD (this catches boolean overwrite immediately)
        if isinstance(cache, bool):
            raise TypeError(
                f"[CACHE OVERWRITE BUG] cache became bool at row {i}"
            )

        if not isinstance(cache, dict):
            raise TypeError(
                f"[CACHE TYPE BREAK] expected dict, got {type(cache)} at row {i}"
            )

        for stmt in plan:
            key = _dedupe_key(stmt)

            if key in seen:
                continue

            seen.add(key)
            plan_all.append(stmt)

        if i % 50 == 0:
            print(f"{i}/{total}")

    # FINAL GUARD BEFORE PERSIST
    if not isinstance(cache, dict):
        raise TypeError(f"[FATAL] cache invalid before save: {type(cache)}")

    save_cache(cache)

    executor = EXECUTORS[mode]()
    executor.setup()
    executor.process(plan_all)