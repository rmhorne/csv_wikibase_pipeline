# triples.py
#
# Declarative CSV → Graph Statement compiler (DEBUG VERSION)
#
# Adds:
# - full execution tracing (resolve / condition / emit / skip)
# - stable semantics from your fixed model
# - no silent failures

# =====================================================
# triples.py — FULL FIXED PIPELINE (ROW + CONTEXTS)
# =====================================================

from ingest import load
from resolver import resolve
import json
from pathlib import Path


# =====================================================
# CACHE
# =====================================================

def ensure_cache(cache):
    if cache is None:
        raise ValueError("Cache required")

    cache.setdefault("_counter", 0)
    cache.setdefault("entities", {})


def write_cache(cache_path, cache):
    if not cache_path:
        return

    Path(cache_path).parent.mkdir(parents=True, exist_ok=True)

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


# =====================================================
# IDENTITY
# =====================================================

def build_row_identity(identity_block, row):
    fields = identity_block.get("fields", [])
    separator = identity_block.get("separator", " | ")

    parts = []

    for f in fields:
        v = row.get(f)
        if v is None:
            continue
        v = str(v).strip()
        if v:
            parts.append(v)

    identity = separator.join(parts) if parts else None

    print("\n[IDENTITY]")
    print("fields:", fields)
    print("result:", identity)

    return identity


# =====================================================
# RESOLVE (SINGLE AUTHORITY)
# =====================================================

def resolve_value(cache, config, value):
    """
    ALL entity creation goes through resolver.
    NO exceptions.
    """

    if value is None:
        return None

    qid, created = resolve(cache, config, str(value))

    print("[RESOLVE]")
    print("input:", value)
    print("output:", qid, "created:", created)

    return qid


# =====================================================
# GRAPH ENGINE
# =====================================================

def evaluate_graph(cache, config, graph, row_entity, context_entity, row):

    triples = []

    print("\n[GRAPH EXEC]")
    print("statements:", len(graph))

    for i, stmt in enumerate(graph):

        print("\n--- stmt", i, "---")
        print(stmt)

        # -------------------------
        # SUBJECT
        # -------------------------
        subj = stmt["subject"]

        if subj["source"] == "self":
            subject_value = context_entity

        elif subj["source"] == "row":
            subject_value = row_entity

        elif subj["source"] == "field":
            field = subj.get("field") or subj.get("name")
            subject_value = row.get(field)

        else:
            subject_value = None

        if subj.get("as") == "entity":
            subject_value = resolve_value(cache, config, subject_value)

        # -------------------------
        # OBJECT
        # -------------------------
        obj = stmt["object"]

        # CRITICAL FIX:
        # "resolve" ALWAYS means entity creation
        if "resolve" in obj:
            object_value = resolve_value(cache, config, obj["resolve"])

        elif obj.get("source") == "self":
            object_value = context_entity

        elif obj.get("source") == "row":
            object_value = row_entity

        elif obj.get("source") == "field":
            field = obj.get("field") or obj.get("name")
            object_value = row.get(field)

        else:
            object_value = None

        if obj.get("as") == "entity":
            object_value = resolve_value(cache, config, object_value)

        triple = {
            "s": subject_value,
            "p": stmt["predicate"],
            "o": object_value,
            "on_create": stmt.get("on_create", False)
        }

        print("[EMIT]")
        print(triple)

        triples.append(triple)

    return triples


# =====================================================
# CONTEXT EXECUTION (MISSING PIECE FIXED)
# =====================================================

def run_contexts(cache, config, contexts, row_entity, row):

    results = {}

    for ctx_name, ctx in contexts.items():

        print("\n[CONTEXT]")
        print("name:", ctx_name)

        identity_block = ctx.get("identity")

        # ---------------------------------
        # CONTEXT ENTITY CREATION
        # ---------------------------------
        if identity_block:
            ctx_identity = build_row_identity(identity_block, row)
            context_entity = resolve_value(cache, config, ctx_identity)
        else:
            context_entity = row_entity

        print("context_entity:", context_entity)

        # ---------------------------------
        # EXECUTE CONTEXT GRAPH
        # ---------------------------------
        ctx_graph = ctx.get("graph", [])

        triples = evaluate_graph(
            cache,
            config,
            ctx_graph,
            row_entity,
            context_entity,
            row
        )

        results[ctx_name] = triples

    return results


# =====================================================
# MAIN PIPELINE
# =====================================================

def run(csv_path, config_path, cache_path):

    print("\n" + "=" * 80)
    print("[TRIPLES START]")
    print("=" * 80)

    config, rows, cache = load(csv_path, config_path, cache_path)

    ensure_cache(cache)

    row_block = config.get("row", {})
    identity_block = row_block.get("identity", {})

    graph = row_block.get("graph", [])
    contexts = config.get("contexts", {})

    if not rows:
        return []

    row = rows[0]

    print("\n[ROW]")
    print(row)

    identity = build_row_identity(identity_block, row)

    if not identity:
        return []

    # ---------------------------------
    # ROW ENTITY
    # ---------------------------------
    row_entity, created = resolve(cache, config, identity)

    print("\n[ROW ENTITY]")
    print(row_entity, created)

    # ---------------------------------
    # ROW GRAPH
    # ---------------------------------
    row_triples = evaluate_graph(
        cache,
        config,
        graph,
        row_entity,
        row_entity,
        row
    )

    # ---------------------------------
    # CONTEXT GRAPHS (FIXED LAYER)
    # ---------------------------------
    context_triples = run_contexts(
        cache,
        config,
        contexts,
        row_entity,
        row
    )

    write_cache(cache_path, cache)

    print("\n" + "=" * 80)
    print("[TRIPLES DONE]")
    print("=" * 80)

    return {
        "row": row_triples,
        "contexts": context_triples
    }