from plan import Statement
from resolver import resolve, resolve_row
from utils import normalize, key


def build_plan(row, config, cache):
    statements = []
    source = config["source"]

    row_level = config["input"]["root"]

    # -------------------------
    # ROW KEY (CONFIG DRIVEN)
    # -------------------------
    if "row_key" in config:
        parts = []
        for f in config["row_key"]["fields"]:
            v = normalize(row.get(f))
            if v:
                parts.append(v)
        row_key = config["row_key"]["separator"].join(parts)
    else:
        row_key = normalize(row.get(config["row_label"]["field"]))

    row_id, _ = resolve_row(row_level, row_key, cache)

    # LABEL
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
    # FRBR CHAIN (GENERIC LEVEL LINKING)
    # -------------------------
    for node in config.get("frbr_chain", []):
        target_level = node["to"]["level"]

        parts = []
        for f in node["match_fields"]:
            v = normalize(row.get(f))
            if v:
                parts.append(v)

        if not parts:
            continue

        target_key = key(" | ".join(parts))
        target_id, _ = resolve(target_level, target_key, cache)

        statements.append(Statement(
            subject=row_id,
            subject_label=row_label,
            predicate=node["predicate"],
            predicate_label=f"{row_level}:{target_level}",
            object=target_id,
            object_label=None,
            object_type="entity",
            source=source
        ))

    # -------------------------
    # FIELD MAPPING
    # -------------------------
    for field, spec in config["fields"].items():
        val = normalize(row.get(field))
        if not val:
            continue

        field_level = spec["frbr"]["level"]

        # -------------------------
        # FLAG FIELDS
        # -------------------------
        if spec.get("match") == "x":
            if str(val).lower() != "x":
                continue

            entity_label = spec.get("value", field)
            qid, _ = resolve(field_level, entity_label, cache)

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

                qid, _ = resolve(field_level, p, cache)

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