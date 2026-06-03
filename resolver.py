from utils import normalize_text, normalize_key


def _bucket(cache, field_type):
    """
    HARD GUARD:
    cache MUST be dict
    """
    if not isinstance(cache, dict):
        raise TypeError(f"Cache corrupted: expected dict, got {type(cache)}")

    cache.setdefault("entities_by_type", {})
    cache["entities_by_type"].setdefault(field_type, {})
    return cache["entities_by_type"][field_type]


def resolve_or_create(label, cache, field_type="entity"):
    """
    Deterministic entity resolver.

    RULES:
    - NO row dependency
    - NO FRBR dependency
    - ONLY normalized label + type
    """

    label_clean = normalize_text(label)
    if not label_clean:
        return None, False

    key = normalize_key(f"{label_clean}|{field_type}")
    bucket = _bucket(cache, field_type)

    if key in bucket:
        return bucket[key], False

    # deterministic ID generation (stable across runs per cache state)
    cache.setdefault("_entity_counter", 1000)
    cache["_entity_counter"] += 1

    qid = f"Q{cache['_entity_counter']}"

    bucket[key] = qid
    return qid, True


def resolve_expression(system_id, cache, prefix="QW"):
    """
    CRITICAL FIX:

    Expression identity is now ONLY system_id-based.

    NO row hashing. NO dict serialization. NO leakage.
    """

    cache.setdefault("expressions", {})

    # already resolved
    if system_id in cache["expressions"]:
        return cache["expressions"][system_id], False

    cache.setdefault("_expr_counter", 1000)
    cache["_expr_counter"] += 1

    qid = f"{prefix}{cache['_expr_counter']}"

    cache["expressions"][system_id] = qid

    return qid, True


def get_expression(cache, system_id):
    return cache.get("expressions", {}).get(system_id)