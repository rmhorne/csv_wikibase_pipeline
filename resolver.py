from utils import normalize


def apply_strategy(values, strategy, separator=" | "):
    """
    Convert raw field values into a deterministic identity key.
    """

    values = [normalize(v) for v in values if normalize(v) is not None]

    if not values:
        return None

    if strategy == "exact":
        return separator.join(values)

    if strategy == "canonicalize":
        cleaned = [v.lower().strip() for v in values]
        cleaned = [v for v in cleaned if v]
        return separator.join(cleaned)

    if strategy == "structured":
        return tuple(values)

    if strategy == "always_new":
        return separator.join(values) + f"::{id(values)}"

    return separator.join(values)


# =====================================================
# SAFE CACHE INIT
# =====================================================

def _ensure_cache(cache):
    if cache is None:
        raise ValueError("Cache object is required")

    cache.setdefault("_counter", 0)
    cache.setdefault("levels", {})


# =====================================================
# CORE RESOLVER
# =====================================================

def resolve(level: str, identity_key: str, cache: dict):
    """
    Identity-based resolver using scoped cache buckets.

    Guarantees:
    - stable ID per (level, identity_key)
    - automatic creation if missing
    - global counter uniqueness
    """

    _ensure_cache(cache)

    # NULL identity → always new node
    if identity_key is None:
        cache["_counter"] += 1
        qid = f"QW{cache['_counter']}"
        return qid, True

    # scoped bucket
    cache["levels"].setdefault(level, {})
    bucket = cache["levels"][level]

    # existing entity
    if identity_key in bucket:
        return bucket[identity_key], False

    # create new entity
    cache["_counter"] += 1
    qid = f"QW{cache['_counter']}"
    bucket[identity_key] = qid

    return qid, True