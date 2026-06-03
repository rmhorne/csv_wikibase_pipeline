from utils import load_json_file, write_json_file, CACHE_FILE


def load_cache():
    """
    Loads persistent pipeline state.

    Core design:
    - expressions: QW-level row entities (primary graph nodes)
    - entities_by_type: resolved Wikibase/QID cache
    - works: legacy compatibility layer (may be phased out later)
    - _qw_counter: global expression ID generator
    """

    if CACHE_FILE.exists():
        cache = load_json_file(CACHE_FILE)
    else:
        cache = {}

    if not isinstance(cache, dict):
        raise TypeError(f"Cache file corrupted: expected dict, got {type(cache)}")

    cache.setdefault("works", {})
    cache.setdefault("entities_by_type", {})
    cache.setdefault("expressions", {})
    cache.setdefault("_qw_counter", 1000)
    cache.setdefault("_schema_version", 1)

    return cache


def save_cache(cache):
    """
    Persists full pipeline state.

    CRITICAL FIX:
    - NEVER return anything
    - NEVER mutate caller's reference
    - NEVER allow accidental reassignment chains
    """

    if not isinstance(cache, dict):
        raise TypeError(f"Refusing to save invalid cache type: {type(cache)}")

    write_json_file(cache, CACHE_FILE)

    # hard safety: explicit return None
    return None