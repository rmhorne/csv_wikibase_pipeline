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


def resolve(level: str, identity_key: str, cache: dict):
    """
    Identity-based resolver using scoped cache buckets.
    """

    if identity_key is None:
        cache["_counter"] += 1
        return f"QW{cache['_counter']}", True

    cache["levels"].setdefault(level, {})
    bucket = cache["levels"][level]

    if identity_key in bucket:
        return bucket[identity_key], False

    cache["_counter"] += 1
    qid = f"QW{cache['_counter']}"
    bucket[identity_key] = qid

    return qid, True