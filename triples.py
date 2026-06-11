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
# CONTEXT RESOLUTION
# =====================================================

def resolve_contexts(row, config, cache, row_id, row_label):
    context_map = {}

    row_level = config["row"].get(
        "context",
        next(iter(config.get("contexts", {})), None)
    )

    if row_level is None:
        raise ValueError("No contexts defined in config; cannot resolve row context.")

    context_map[row_level] = {
        "id": row_id,
        "label": row_label
    }

    for name, spec in config.get("contexts", {}).items():

        identity_key = build_identity(row, spec["identity"])
        if not identity_key:
            continue

        label_field = spec.get("label", {}).get("field")
        label = normalize(row.get(label_field)) if label_field else None

        ctx_qid, _ = resolve(name, identity_key, cache)

        context_map[name] = {
            "id": ctx_qid,
            "label": label
        }

    return context_map


# =====================================================
# ENTITY REGISTRY (FINAL HARD FIX)
# =====================================================

def build_entity_registry(row, config, cache):
    registry = {}

    for field, spec in config.get("fields", {}).items():

        raw = row.get(field)

        if raw is None:
            continue

        raw = normalize(raw)
        if not raw:
            continue

        # -------------------------------------------------
        # RULE 1: NEVER register condition fields
        # -------------------------------------------------
        if spec.get("condition"):
            continue

        # -------------------------------------------------
        # RULE 2: NEVER register literal-only fields
        # (this is what you were screaming about)
        # -------------------------------------------------
        if spec.get("graph"):
            is_literal_only = True
            for g in spec["graph"]:
                if g.get("subject", {}).get("as") != "literal" and \
                   g.get("object", {}).get("as") != "literal":
                    is_literal_only = False
                    break
            if is_literal_only:
                continue

        if spec.get("on_create"):
            is_literal_only = True
            for c in spec["on_create"]:
                obj = c.get("object", {})
                if obj.get("as") != "literal":
                    is_literal_only = False
                    break
            if is_literal_only:
                continue

        # -------------------------------------------------
        # SPLIT HANDLING
        # -------------------------------------------------
        if spec.get("split"):
            values = [
                normalize(v)
                for v in raw.split(spec.get("delimiter", ";"))
                if normalize(v)
            ]
        else:
            values = [raw]

        scope = spec.get("scope", field)

        for v in values:
            obj_id, _ = resolve(scope, v, cache)

            registry[(field, v)] = {
                "id": obj_id,
                "label": v
            }

    return registry


# =====================================================
# NODE RESOLUTION
# =====================================================

def resolve_node(node_spec, row_id, context_map, entity_registry, field, value):
    if not node_spec:
        return None

    # HARD RULE: literal never produces entities
    if node_spec.get("as") == "literal":
        return None

    source = node_spec.get("source")

    if source == "self":
        node = entity_registry.get((field, value))
        return node["id"] if node else None

    if source == "field":
        return field

    if source == "context":
        ctx = node_spec.get("context")
        return context_map.get(ctx, {}).get("id")

    if source == "row":
        return row_id

    if source == "constant":
        return node_spec.get("value")

    return None


# =====================================================
# LABEL RESOLUTION
# =====================================================

def resolve_label(node_spec, row_id, context_map, entity_registry, field, value, row_label):
    if not node_spec:
        return None

    if node_spec.get("as") == "literal":
        return value

    source = node_spec.get("source")

    if source == "self":
        node = entity_registry.get((field, value))
        return node["label"] if node else None

    if source == "field":
        return field

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
# MAIN PLAN BUILDER
# =====================================================

def build_plan(row, config, cache, row_index=None):
    statements = []

    row_level = config["row"].get(
        "context",
        next(iter(config.get("contexts", {})))
    )

    row_id = build_identity(row, config["row"]["identity"])
    row_label = normalize(row.get(config["row"]["label"]["field"]))

    row_qid, _ = resolve(row_level, row_id, cache)

    context_map = resolve_contexts(row, config, cache, row_qid, row_label)

    # -------------------------------------------------
    # ROW LABEL
    # -------------------------------------------------
    if row_label:
        statements.append(Statement(
            subject=row_qid,
            subject_label=row_label,
            predicate="LABEL",
            predicate_label="LABEL",
            object=None,
            object_label=None,
            object_type="literal",
            source=config["source"],
            provenance=row_index
        ))

    # -------------------------------------------------
    # ENTITY REGISTRY (FIXED)
    # -------------------------------------------------
    entity_registry = build_entity_registry(row, config, cache)

    # -------------------------------------------------
    # FIELD PROCESSING
    # -------------------------------------------------
    for field, spec in config.get("fields", {}).items():

        raw = row.get(field)
        if raw is None:
            continue

        raw = normalize(raw)
        if not raw:
            continue

        # condition only affects processing, NOT registry
        condition = spec.get("condition")
        if condition and condition.get("source") == "self":
            if str(raw).lower() != str(condition.get("value", "")).lower():
                continue

        if spec.get("split"):
            values = [
                normalize(v)
                for v in raw.split(spec.get("delimiter", ";"))
                if normalize(v)
            ]
        else:
            values = [raw]

        for v in values:
            v = normalize(v)
            if not v:
                continue

            for g in spec.get("graph", []):

                subject = resolve_node(
                    g.get("subject"),
                    row_qid,
                    context_map,
                    entity_registry,
                    field,
                    v
                )

                obj = resolve_node(
                    g.get("object"),
                    row_qid,
                    context_map,
                    entity_registry,
                    field,
                    v
                )

                if subject is None:
                    subject = row_qid

                if obj is None and g.get("object", {}).get("as") != "literal":
                    obj = v

                statements.append(Statement(
                    subject=subject,
                    subject_label=resolve_label(
                        g.get("subject"),
                        row_qid,
                        context_map,
                        entity_registry,
                        field,
                        v,
                        row_label
                    ),
                    predicate=g.get("predicate", field),
                    predicate_label=field,
                    object=obj,
                    object_label=resolve_label(
                        g.get("object"),
                        row_qid,
                        context_map,
                        entity_registry,
                        field,
                        v,
                        row_label
                    ),
                    object_type="literal" if g.get("object", {}).get("as") == "literal" else "entity",
                    source=config["source"],
                    references=[],
                    qualifiers=[],
                    provenance=row_index
                ))

    return statements, cache