from plan import Statement
from resolver import resolve
from utils import normalize


# =====================================================
# IDENTITY BUILDER
# =====================================================

def build_identity(row, identity_spec):
    fields = identity_spec.get("fields", [])
    separator = identity_spec.get("separator", " | ")
    strategy = identity_spec.get("strategy", "exact")

    values = [row.get(f) for f in fields]

    from resolver import apply_strategy
    return apply_strategy(values, strategy, separator)


# =====================================================
# CONTEXT NODE BUILD (FRBR LAYER)
# =====================================================

def resolve_contexts(row, config, cache):
    context_map = {}

    row_level = config["row"]["context"]

    row_id = build_identity(row, config["row"]["identity"])
    row_label = normalize(row.get(config["row"]["label"]["field"]))

    row_qid, _ = resolve(row_level, row_id, cache)
    context_map[row_level] = {
        "id": row_qid,
        "label": row_label
    }

    for ctx in config.get("contexts", []):
        name = ctx["name"]

        identity_key = build_identity(row, ctx["identity"])
        if not identity_key:
            continue

        label_field = ctx.get("label", {}).get("field")
        label = normalize(row.get(label_field)) if label_field else None

        ctx_qid, _ = resolve(name, identity_key, cache)

        context_map[name] = {
            "id": ctx_qid,
            "label": label
        }

    return context_map, row_id, row_label


# =====================================================
# PHASE 1: BUILD ENTITY REGISTRY (ALL COLUMN ENTITIES)
# =====================================================

def build_entity_registry(row, config, cache):
    registry = {}

    for field, spec in config["fields"].items():

        raw = normalize(row.get(field))
        if not raw:
            continue

        if spec.get("split"):
            values = [
                normalize(v)
                for v in raw.split(spec.get("delimiter", ";"))
                if normalize(v)
            ]
        else:
            values = [raw]

        scope = spec.get("scope", "entity")

        for v in values:
            obj_id, _ = resolve(scope, v, cache)

            # STORE LABEL + ID TOGETHER
            registry[(field, v)] = {
                "id": obj_id,
                "label": v
            }

    return registry


# =====================================================
# NODE RESOLUTION (PURE LOOKUP ONLY)
# =====================================================

def resolve_node(node_spec, row_id, context_map, entity_registry, field, value):
    if not node_spec:
        return None

    source = node_spec.get("source")

    # COLUMN → ENTITY
    if source == "column":
        node = entity_registry.get((field, value))
        return node["id"] if node else None

    # CONTEXT → FRBR NODE
    if source == "context":
        ctx = node_spec.get("context")
        return context_map.get(ctx, {}).get("id")

    # ROW → FRBR ROW NODE
    if source == "row":
        return row_id

    # CONSTANT
    if source == "constant":
        return node_spec.get("value")

    return None


# =====================================================
# LABEL RESOLUTION (CRITICAL FIX)
# =====================================================

def resolve_label(node_spec, row_id, context_map, entity_registry, field, value, row_label):
    """
    Determines correct label based on node type.
    """
    if not node_spec:
        return None

    source = node_spec.get("source")

    if source == "column":
        node = entity_registry.get((field, value))
        return node["label"] if node else None

    if source == "context":
        ctx = node_spec.get("context")
        node = context_map.get(ctx)
        return node["label"] if node else None

    if source == "row":
        return row_label

    if source == "constant":
        return node_spec.get("value")

    return None


# =====================================================
# FIELD EXECUTION (EDGE EMISSION ONLY)
# =====================================================

def build_plan(row, config, cache):
    statements = []

    # -------------------------------------------------
    # CONTEXT NODES (FRBR LAYER)
    # -------------------------------------------------
    context_map, row_id, row_label = resolve_contexts(row, config, cache)

    row_level = config["row"]["context"]

    # -------------------------------------------------
    # ROW LABEL EDGE
    # -------------------------------------------------
    if row_label:
        statements.append(Statement(
            subject=row_id,
            subject_label=row_label,
            predicate="LABEL",
            predicate_label="LABEL",
            object=None,
            object_label=None,
            object_type="literal",
            source=config["source"]
        ))

    # -------------------------------------------------
    # ENTITY REGISTRY
    # -------------------------------------------------
    entity_registry = build_entity_registry(row, config, cache)

    # -------------------------------------------------
    # EDGE EMISSION ONLY
    # -------------------------------------------------
    for field, spec in config["fields"].items():

        raw = normalize(row.get(field))
        if not raw:
            continue

        if spec.get("match") == "x":
            if str(raw).lower() != "x":
                continue
            values = [field]
        else:
            values = (
                raw.split(spec.get("delimiter", ";"))
                if spec.get("split")
                else [raw]
            )

        graph_rules = spec.get("graph") or []

        for v in values:
            v = normalize(v)
            if not v:
                continue

            for g in graph_rules:

                subject = resolve_node(
                    g.get("subject"),
                    row_id,
                    context_map,
                    entity_registry,
                    field,
                    v
                )

                obj = resolve_node(
                    g.get("object"),
                    row_id,
                    context_map,
                    entity_registry,
                    field,
                    v
                )

                # FALLBACKS ONLY
                if subject is None:
                    subject = row_id
                if obj is None:
                    node = entity_registry.get((field, v))
                    obj = node["id"] if node else v

                # 🔥 FIXED LABEL LOGIC (THIS IS THE BUG YOU HIT)
                subject_label = resolve_label(
                    g.get("subject"),
                    row_id,
                    context_map,
                    entity_registry,
                    field,
                    v,
                    row_label
                )

                object_label = resolve_label(
                    g.get("object"),
                    row_id,
                    context_map,
                    entity_registry,
                    field,
                    v,
                    row_label
                )

                statements.append(Statement(
                    subject=subject,
                    subject_label=subject_label,
                    predicate=g.get("predicate", spec.get("predicate", field)),
                    predicate_label=field,
                    object=obj,
                    object_label=object_label,
                    object_type=spec["type"],
                    source=config["source"]
                ))

    return statements, cache