from .wiki_reconcile_client import WikiReconcileClient
import time


def build_reconciliation_map(records, config):
    client = WikiReconcileClient(config)

    result = {}

    total = len(records)
    print(f"[apply] start: {total} rows", flush=True)

    for i, row in enumerate(records, 1):
        label = row.get("name")
        local_id = row.get("id")

        if not label or not local_id:
            continue

        print(f"[apply] {i}/{total} {label}", flush=True)

        t0 = time.time()
        candidates = client.search(label, limit=5)
        dt = time.time() - t0

        print(f"[apply] → {len(candidates)} in {dt:.2f}s", flush=True)

        seen = set()
        deduped = []

        for c in candidates:
            if c["id"] in seen:
                continue
            seen.add(c["id"])
            deduped.append(c)

        deduped.append({
            "id": "__create__",
            "label": label
        })

        result[local_id] = {
            "label": label,
            "candidates": deduped
        }

    print("[apply] done", flush=True)
    return result