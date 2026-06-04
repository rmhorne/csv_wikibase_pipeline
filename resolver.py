from utils import key


def resolve(level: str, label: str, cache: dict):
    """
    Universal resolver:
    - level comes from config
    - label defines identity
    """

    k = key(label)
    if not k:
        return None, False

    cache["levels"].setdefault(level, {})

    bucket = cache["levels"][level]

    if k in bucket:
        return bucket[k], False

    cache["_counter"] += 1
    qid = f"QW{cache['_counter']}"

    bucket[k] = qid
    return qid, True


def resolve_row(level: str, row_key: str, cache: dict):
    """
    Row is just another level in the same system.
    """
    k = key(row_key)
    if not k:
        cache["_counter"] += 1
        return f"QW{cache['_counter']}", True

    cache["levels"].setdefault(level, {})
    bucket = cache["levels"][level]

    if k in bucket:
        return bucket[k], False

    cache["_counter"] += 1
    qid = f"QW{cache['_counter']}"
    bucket[k] = qid
    return qid, True