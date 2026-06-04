from plan import Statement
from resolver import resolve, resolve_row
from utils import normalize, key


# -----------------------------
# SAFE CONFIG HELPERS
# -----------------------------

def get_field_level(spec, default_level):
    """
    Supports BOTH:
    - old: spec["frbr"]["level"]
    - new: graph-based (no frbr at all)
    """
    if isinstance(spec.get("frbr"), dict):
        return spec["frbr"].get("level", default_level)

    return default_level


def get_predicate(spec, graph_node=None):
    """
    Predicate priority:
    1. graph.node["predicate"]
    2. spec["predicate"]
    3. None (skip safely)
    """
    if graph_node and "predicate" in graph_node:
        return graph_node["predicate"]

    return spec.get("predicate")


def get_level_from_node(node, default):
    if isinstance(node, dict) and "level" in node:
        return node["level"]
    return default


# -----------------------------
# MAIN BUILDER
# -----------------------------

def build_plan(row, config, cache):
    statements = []
    source = config["source"]

    row_level = config["input"]["root"]

    # -------------------------
    # ROW KEY
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

    # -------------------------
    # LABEL
    # -------------------------
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

    # =====================================================
    # FRBR CHAIN (SAFE LEGACY SUPPORT)
    # =====================================================
    for node in config.get("frbr_chain", []):
        target_level = node["to"]["level"]

        parts = []
        for f in node.get("match_fields", []):
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
            predicate=node.get("predicate", "UNKNOWN"),
            predicate_label=f"{row_level}:{target_level}",
            object=target_id,
            object_label=None,
            object_type="entity",
            source=source
        ))

    # =====================================================
    # FIELD MAPPING (GRAPH-FIRST SYSTEM)
    # =====================================================
    for field, spec in config["fields"].items():

        val = normalize(row.get(field))
        if not val:
            continue

        field_level = get_field_level(spec, row_level)

        # -------------------------
        # FLAG FIELDS (x match)
        # -------------------------
        if spec.get("match") == "x":
            if str(val).lower() != "x":
                continue

            entity_label = spec.get("value", field)
            qid, _ = resolve(field_level, entity_label, cache)

            statements.append(Statement(
                subject=row_id,
                subject_label=row_label,
                predicate=spec.get("predicate", field),
                predicate_label=field,
                object=qid,
                object_label=entity_label,
                object_type="entity",
                source=source
            ))
            continue

        # -------------------------
        # GRAPH-BASED MODEL (PRIMARY PATH)
        # -------------------------
        graph = spec.get("graph", [])

        if graph:
            # entity fields with graph logic
            if spec.get("type") == "entity":

                parts = (
                    val.split(spec.get("delimiter", ";"))
                    if spec.get("split")
                    else [val]
                )

                for p in parts:
                    p = normalize(p)
                    if not p:
                        continue

                    entity_id, _ = resolve(field_level, p, cache)

                    # base row → entity
                    statements.append(Statement(
                        subject=row_id,
                        subject_label=row_label,
                        predicate=spec.get("predicate", field),
                        predicate_label=field,
                        object=entity_id,
                        object_label=p,
                        object_type="entity",
                        source=source
                    ))

                    # -------------------------
                    # GRAPH EDGES
                    # -------------------------
                    for g in graph:

                        from_level = get_level_from_node(g.get("from"), row_level)
                        if from_level != "row":
                            continue

                        to_node = g.get("to", {})

                        # key derivation logic
                        if to_node.get("key_from_value"):
                            target_label = p
                        elif "value" in to_node:
                            target_label = to_node["value"]
                        elif to_node.get("entity_type"):
                            target_label = to_node["entity_type"]
                        else:
                            target_label = field

                        target_level = get_level_from_node(to_node, field_level)

                        target_id, _ = resolve(target_level, target_label, cache)

                        statements.append(Statement(
                            subject=entity_id,
                            subject_label=p,
                            predicate=get_predicate(spec, g),
                            predicate_label=field,
                            object=target_id,
                            object_label=target_label,
                            object_type="entity",
                            source=source
                        ))

            # literal fields with graph support
            else:
                for g in graph:
                    from_level = get_level_from_node(g.get("from"), row_level)
                    if from_level != "row":
                        continue

                    to_level = get_level_from_node(g.get("to"), field_level)
                    predicate = get_predicate(spec, g)

                    if not predicate:
                        continue

                    statements.append(Statement(
                        subject=row_id,
                        subject_label=row_label,
                        predicate=predicate,
                        predicate_label=field,
                        object=val,
                        object_label=None,
                        object_type="literal",
                        source=source
                    ))

        # -------------------------
        # LEGACY MODE (NO GRAPH)
        # -------------------------
        else:
            if "predicate" not in spec:
                continue  # safe skip instead of crash

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