from utils import identity_key


def _boot(cache):
    cache.setdefault("_counter", 0)
    cache.setdefault("entities", {})


def is_qid(value):
    return isinstance(value, str) and value.startswith("Q")


def resolve(cache, config, label):
    """
    GLOBAL ENTITY RESOLVER

    RULE:
    - NEVER re-resolve QIDs
    - ONLY raw labels are accepted
    """

    _boot(cache)

    if label is None:
        return None, False

    # 🚨 CRITICAL GUARD: DO NOT RE-RESOLVE QIDs
    if is_qid(label):
        return label, False

    key = identity_key(label)
    if key is None:
        return None, False

    if key in cache["entities"]:
        return cache["entities"][key], False

    cache["_counter"] += 1
    prefix = config["source"]["id_prefix"]

    qid = f"{prefix}{cache['_counter']}"

    cache["entities"][key] = qid

    return qid, True