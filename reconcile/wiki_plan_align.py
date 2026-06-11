import json


# =========================================================
# IO
# =========================================================
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# =========================================================
# CORE REWRITE LOGIC (UNCHANGED)
# =========================================================
def resolve_qw(qw, mapping):
    """
    Convert QW id → QID if possible.
    Otherwise leave unchanged.
    """
    if isinstance(qw, str) and qw in mapping:
        return mapping[qw]["qid"]
    return qw


def rewrite_value(value, mapping):
    """
    Recursively rewrite values in plan structure.
    """

    if isinstance(value, str):
        return resolve_qw(value, mapping)

    if isinstance(value, list):
        return [rewrite_value(v, mapping) for v in value]

    if isinstance(value, dict):
        return {k: rewrite_value(v, mapping) for k, v in value.items()}

    return value


def rewrite_plan(plan, mapping):
    """
    ORIGINAL BEHAVIOR.
    Leave this intact for backwards compatibility.
    """
    return rewrite_value(plan, mapping)


# =========================================================
# ALIGNMENT HELPERS
# =========================================================
def collect_qws(value, found=None):

    if found is None:
        found = set()

    if isinstance(value, str):
        if value.startswith("QW"):
            found.add(value)

    elif isinstance(value, list):
        for v in value:
            collect_qws(v, found)

    elif isinstance(value, dict):
        for v in value.values():
            collect_qws(v, found)

    return found


def statement_status(statement, mapping):

    qws = collect_qws(statement)

    if not qws:
        return "skipped", []

    missing = sorted(
        qw for qw in qws
        if qw not in mapping
    )

    if missing:
        return "failure", missing

    return "success", []


def split_plan(plan, mapping):

    aligned = []
    unaligned = []
    status = []

    for statement in plan:

        state, missing = statement_status(statement, mapping)

        status.append({
            "status": state,
            "missing": missing
        })

        if state == "success":
            aligned.append(
                rewrite_value(statement, mapping)
            )

        elif state == "failure":
            unaligned.append(statement)

    return aligned, unaligned, status