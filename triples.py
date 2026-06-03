from resolver import resolve_or_create, resolve_expression
from plan import Statement
from utils import normalize_text, normalize_key
from frbr import build_frbr_chain, get_frbr_level, get_frbr_predicate


# -----------------------------
# validation
# -----------------------------

def _valid(val):
    if val is None:
        return False

    if not isinstance(val, str):
        val = str(val)

    v = normalize_text(val)

    if v is None:
        return False

    v = v.strip()

    if not v:
        return False

    if v.lower() in {"nan", "none", "null"}:
        return False

    return True


# -----------------------------
# split helper
# -----------------------------

def _split(val, spec):
    if not spec.get("split"):
        return [val]

    if not _valid(val):
        return []

    delimiter = spec.get("delimiter", ";")
    parts = val.split(delimiter)

    return [normalize_text(p) for p in parts if _valid(p)]


# -----------------------------
# SYSTEM ID
# -----------------------------

def _get_system_id(config, cache):
    cache.setdefault("_system_counter", 1000)
    cache["_system_counter"] += 1

    prefix = config["input"]["id_prefix"]

    return f"{prefix}{cache['_system_counter']}"


# -----------------------------
# LABEL
# -----------------------------

def _build_row_label(row, config):
    cfg = config.get("row_label") or config.get("expression_label", {})
    field = cfg.get("field")

    if not field:
        return None

    v = row.get(field)

    if v is None:
        return None

    v = normalize_text(v)

    if not v:
        return None

    return v


def _build_work_key(row, config):
    cfg = config.get("work_key", {})
    fields = cfg.get("fields") or []

    if not fields:
        return None

    separator = cfg.get("separator", "|")
    values = [normalize_text(row.get(field), allow_empty=True) or "" for field in fields]

    if not any(values):
        return None

    return normalize_key(separator.join(values))


# -----------------------------
# WORK RESOLUTION
# -----------------------------

def _resolve_work(row, config, cache):
    """
    Uses frbr_chain.match_fields
    instead of obsolete work_key_columns.
    """

    frbr_chain = config.get("frbr_chain", [])

    for node in frbr_chain:

        if node.get("to", {}).get("level") != "work":
            continue

        match_fields = node.get("match_fields", ["Title"])

        values = []

        for field in match_fields:
            v = normalize_text(row.get(field))

            if _valid(v):
                values.append(v)

        if not values:
            continue

        work_label = normalize_key("|".join(values))

        work_qid, created = resolve_or_create(
            work_label,
            cache,
            field_type="work"
        )

        cache.setdefault("works", {})
        cache["works"][work_label] = work_qid

        return (
            work_label,
            work_qid,
            created,
            node
        )

    return (
        None,
        None,
        False,
        None
    )


# -----------------------------
# MAIN ENGINE
# -----------------------------

def generate_plan(row, config, cache):
    plan = []

    source = config.get("source", {})

    system_id = _get_system_id(config, cache)

    fields = config["fields"]

    seen = set()

    def emit(stmt):

        if stmt.object is None:
            return

        if isinstance(stmt.object, str) and not _valid(stmt.object):
            return

        key = (
            stmt.subject,
            stmt.predicate,
            stmt.object,
            stmt.object_type
        )

        if key in seen:
            return

        seen.add(key)

        plan.append(stmt)

    # -------------------------
    # LABEL
    # -------------------------

    label = _build_row_label(row, config)

    if label:
        emit(
            Statement(
                subject=system_id,
                predicate="LABEL",
                object=label,
                object_type="literal",
                action="reuse",
                source=source,
                field_type="label"
            )
        )

    # -------------------------
    # WORK RESOLUTION
    # -------------------------

    (
        work_label,
        work_qid,
        work_created,
        work_node
    ) = _resolve_work(
        row,
        config,
        cache
    )

    # -------------------------
    # EXPRESSION
    # -------------------------

    expr_qid, expr_created = resolve_expression(
        system_id,
        cache
    )

    expr_label = _build_row_label(row, config)
    expr_work_key = _build_work_key(row, config) or work_label

    emit(
        Statement(
            subject=system_id,
            predicate="HAS_EXPRESSION",
            object=expr_qid,
            object_type="entity",
            action="create" if expr_created else "reuse",
            qid=expr_qid,
            field_type="expression",
            source=source
        )
    )

    cache.setdefault("expressions_meta", {})

    cache["expressions_meta"][expr_qid] = {
        "system_id": system_id,
        "label": expr_label or system_id,
        "work_key": expr_work_key
    }

    # -------------------------
    # EXPRESSION -> WORK
    # -------------------------

    if work_qid:

        predicate = "P_WORK_LINK"

        if work_node:
            predicate = (
                get_frbr_predicate(work_node)
                or "P_WORK_LINK"
            )

        emit(
            Statement(
                subject=expr_qid,
                predicate=predicate,
                object=work_qid,
                object_type="entity",
                action="create" if work_created else "reuse",
                qid=work_qid,
                field_type="work",
                source=source
            )
        )

    # -------------------------
    # FIELD PROCESSING
    # -------------------------

    for col, spec in fields.items():

        val = row.get(col)

        if not _valid(val):
            continue

        val = normalize_text(val)

        ftype = spec["type"]

        # ---------------------
        # entity trigger
        # ---------------------

        if (
            ftype == "entity"
            and spec.get("match") is not None
        ):

            if val == spec.get("match"):

                v = spec.get("value", val)

                if not _valid(v):
                    continue

                qid, created = resolve_or_create(v, cache)

                emit(
                    Statement(
                        subject=system_id,
                        predicate=spec["predicate"],
                        object=v,
                        object_type="entity",
                        action="create" if created else "reuse",
                        qid=qid,
                        field_type="entity",
                        source=source,
                        qualifiers=[
                            (
                                "certainty",
                                spec.get("certainty")
                            )
                        ] if spec.get("certainty") else []
                    )
                )

            continue

        # ---------------------
        # entity
        # ---------------------

        if ftype == "entity":

            for v in _split(val, spec):

                if not _valid(v):
                    continue

                qid, created = resolve_or_create(
                    v,
                    cache
                )

                emit(
                    Statement(
                        subject=system_id,
                        predicate=spec["predicate"],
                        object=v,
                        object_type="entity",
                        action="create" if created else "reuse",
                        qid=qid,
                        field_type=spec.get(
                            "frbr",
                            {}
                        ).get(
                            "level",
                            "entity"
                        ),
                        source=source
                    )
                )

        # ---------------------
        # literal
        # ---------------------

        elif ftype == "literal":

            for v in _split(val, spec):

                if not _valid(v):
                    continue

                emit(
                    Statement(
                        subject=system_id,
                        predicate=spec["predicate"],
                        object=v,
                        object_type="literal",
                        action="reuse",
                        qid=None,
                        field_type=spec.get(
                            "frbr",
                            {}
                        ).get(
                            "level",
                            "literal"
                        ),
                        source=source
                    )
                )

    return plan, cache