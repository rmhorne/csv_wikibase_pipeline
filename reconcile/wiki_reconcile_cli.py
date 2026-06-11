import argparse
import json
import csv

from .wiki_reconcile_cache import load_cache
from .wiki_reconcile_apply import build_reconciliation_map
from .wiki_reconcile_rewrite import rewrite_plan_with_qids
from .wiki_reconcile_writeback import write_plan_to_wikibase
from .wiki_plan_align import rewrite_plan, load_json, save_json

# =========================================================
# IO HELPERS
# =========================================================
def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# =========================================================
# CLI
# =========================================================
def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")

    exp = sub.add_parser("export")
    exp.add_argument("--cache")
    exp.add_argument("--config")
    exp.add_argument("--out")

    ap = sub.add_parser("apply")
    ap.add_argument("--input")
    ap.add_argument("--config")
    ap.add_argument("--out")

    rw = sub.add_parser("rewrite")
    rw.add_argument("--plan")
    rw.add_argument("--map")
    rw.add_argument("--out")

    wb = sub.add_parser("writeback")
    wb.add_argument("--plan")
    wb.add_argument("--config")

    orp = sub.add_parser("export-openrefine")
    orp.add_argument("--input", required=True)
    orp.add_argument("--json", required=True)
    orp.add_argument("--csv", required=True)


    align = sub.add_parser("align")
    align.add_argument("--plan", required=True)
    align.add_argument("--map", required=True)

    align.add_argument("--out_aligned", required=True)
    align.add_argument("--out_unaligned", required=True)
    align.add_argument("--out_status", required=True)

    args = p.parse_args()

    # =====================================================
    # EXPORT (original pipeline)
    # =====================================================
    if args.cmd == "export":
        print("[cli] export starting", flush=True)

        cache = load_cache(args.cache)
        config = load(args.config)

        from .wiki_reconcile_export import build_reconciliation_export

        out = build_reconciliation_export(cache, config)
        save_json(args.out, out)

        print("[cli] export done", flush=True)

    # =====================================================
    # APPLY
    # =====================================================
    elif args.cmd == "apply":
        print("[cli] apply starting", flush=True)

        data = load(args.input)
        config = load(args.config)

        out = build_reconciliation_map(data, config)
        save_json(args.out, out)

        print("[cli] apply done", flush=True)

    # =====================================================
    # REWRITE
    # =====================================================
    elif args.cmd == "rewrite":
        plan = load(args.plan)
        mapping = load(args.map)

        out = rewrite_plan_with_qids(plan, mapping)
        save_json(args.out, out)

    # =====================================================
    # WRITEBACK
    # =====================================================
    elif args.cmd == "writeback":
        cfg = load(args.config)
        plan = load(args.plan)

        res = write_plan_to_wikibase(
            plan,
            cfg["api_url"],
            auth=(
                cfg["wikibase_auth"]["username"],
                cfg["wikibase_auth"]["password"]
            ) if cfg["wikibase_auth"]["enabled"] else None
        )

        print(json.dumps(res, indent=2))

    # =====================================================
    # OPENREFINE EXPORT (FIXED CLEAN VERSION)
    # =====================================================
    elif args.cmd == "export-openrefine":
        print("[cli] export-openrefine starting", flush=True)

        from .wiki_reconcile_openrefine_export import (
            write_openrefine_json,
            write_openrefine_csv
        )

        records = load(args.input)

        # single responsibility: exporter handles everything
        write_openrefine_json(records, args.json)
        write_openrefine_csv(records, args.csv)

        print(f"[cli] wrote JSON → {args.json}", flush=True)
        print(f"[cli] wrote CSV  → {args.csv}", flush=True)
        print("[cli] export-openrefine done", flush=True)


    elif args.cmd == "align":
        print("[cli] align starting", flush=True)

        plan = load(args.plan)
        mapping = load(args.map)

        from .wiki_plan_align import split_plan

        aligned, unaligned, status = split_plan(
            plan,
            mapping
        )

        save_json(args.out_aligned, aligned)
        save_json(args.out_unaligned, unaligned)
        save_json(args.out_status, status)

        print("[cli] align done", flush=True)



if __name__ == "__main__":
    main()