from plan import Statement
from resolver import resolve_entity, resolve_work, resolve_row
from utils import normalize, key


def build_plan(row, config, cache):
    statements = []
    source = config["source"]

    # -------------------------
    # ROW ENTITY
    # -------------------------
    row_id = resolve_row(cache)
    label_field = config["row_label"]["field"]
    row_label = normalize(row.get(label_field))

    if row_label:
        statements.append(Statement(
            subject=row_id,
            subject_label=row_label,
            predicate="LABEL",
            predicate_label="LABEL",
            object=None,
            object_label=None,
            object_type="literal",
            source=source
        ))

    # -------------------------
    # FRBR CHAIN (WORK)
    # -------------------------
    for node in config.get("frbr_chain", []):
        if node["to"]["level"] != "work":
            continue

        parts = []
        for f in node["match_fields"]:
            v = normalize(row.get(f))
            if v:
                parts.append(v)

        if not parts:
            continue

        work_key = key(" | ".join(parts))
        work_id, created = resolve_work(work_key, cache)

        statements.append(Statement(
            subject=row_id,
            subject_label=row_label,
            predicate=node["predicate"],
            predicate_label="FRBR:work",
            object=work_id,
            object_label=None,
            object_type="entity",
            source=source
        ))

    # -------------------------
    # FIELD MAPPING
    # -------------------------
    for field, spec in config["fields"].items():
        val = row.get(field)
        val = normalize(val)

        if not val:
            continue

        # -------------------------
        # FLAG FIELDS ("x")
        # -------------------------
        if spec.get("match") == "x":
            if val.lower() != "x":
                continue

            entity_label = spec.get("value", field)
            qid, created = resolve_entity(entity_label, cache)

            statements.append(Statement(
                subject=row_id,
                subject_label=row_label,
                predicate=spec["predicate"],
                predicate_label=field,
                object=qid,
                object_label=entity_label,
                object_type="entity",
                source=source
            ))
            continue

        # -------------------------
        # ENTITY FIELDS
        # -------------------------
        if spec["type"] == "entity":
            parts = val.split(spec.get("delimiter", ";")) if spec.get("split") else [val]

            for p in parts:
                p = normalize(p)
                if not p:
                    continue

                qid, created = resolve_entity(p, cache)

                statements.append(Statement(
                    subject=row_id,
                    subject_label=row_label,
                    predicate=spec["predicate"],
                    predicate_label=field,
                    object=qid,
                    object_label=p,
                    object_type="entity",
                    source=source
                ))

        # -------------------------
        # LITERAL FIELDS
        # -------------------------
        else:
            statements.append(Statement(
                subject=row_id,
                subject_label=row_label,
                predicate=spec["predicate"],
                predicate_label=field,
                object=val,
                object_label=None,
                object_type="literal",
                source=source
            ))

    return statements, cache