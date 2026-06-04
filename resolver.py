from utils import key


def resolve_entity(label, cache):
    k = key(label)
    if not k:
        return None, False

    if k in cache["entities"]:
        return cache["entities"][k], False

    cache["_counter"] += 1
    qid = f"QW{cache['_counter']}"

    cache["entities"][k] = qid
    return qid, True


def resolve_work(key_str, cache):
    if not key_str:
        return None, False

    if key_str in cache["work"]:
        return cache["work"][key_str], False

    cache["_counter"] += 1
    qid = f"QW{cache['_counter']}"

    cache["work"][key_str] = qid
    return qid, True


def resolve_row(cache):
    cache["_counter"] += 1
    return f"QW{cache['_counter']}"