from .wiki_reconcile_client import WikiReconcileClient
import re


# ----------------------------
# NORMALIZATION
# ----------------------------
def normalize_label(label):
    if label is None:
        return None

    if isinstance(label, (int, float)):
        return None

    s = str(label).strip()

    # reject pure numbers
    if re.fullmatch(r"\d+(\.\d+)?", s):
        return None

    # strip metadata suffixes
    s = s.split("::")[0]
    s = s.split("|")[0].strip()

    if len(s) < 2:
        return None

    return s


# ----------------------------
# CLASSIFICATION (FAIL-OPEN MODEL)
# ----------------------------
def classify(bucket_name: str, label: str) -> str:
    """
    Default-open reconciliation policy:
    - ALL buckets are processed unless explicitly excluded
    - only invalid labels are filtered
    """

    if label is None:
        return "skip"

    if isinstance(label, (int, float)):
        return "skip"

    s = str(label).strip()

    # skip pure numeric tokens
    if re.fullmatch(r"\d+(\.\d+)?", s):
        return "skip"

    # optional global exclusions (currently empty)
    EXCLUDED_BUCKETS = set()
    if bucket_name in EXCLUDED_BUCKETS:
        return "skip"

    return "entity"


# ----------------------------
# EXPORT PIPELINE
# ----------------------------
def build_reconciliation_export(cache, config):
    client = WikiReconcileClient(config)

    levels = cache.get("levels", {})

    output = []

    total_buckets = len(levels)
    print(f"[export] starting {total_buckets} buckets", flush=True)

    for bucket_name, bucket in levels.items():

        print(f"[export] bucket: {bucket_name} ({len(bucket)})", flush=True)

        for i, (raw_label, local_id) in enumerate(bucket.items(), 1):

            label = normalize_label(raw_label)

            if not label:
                print(f"[export] SKIP bad label: {raw_label}", flush=True)
                continue

            if classify(bucket_name, label) == "skip":
                print(f"[export] SKIP: {bucket_name} :: {label}", flush=True)
                continue

            print(f"[export] querying [{bucket_name}] {i}/{len(bucket)}: {label}", flush=True)

            try:
                candidates = client.search(label, limit=5)
            except Exception as e:
                print(f"[export] ERROR {label}: {e}", flush=True)
                continue

            # deduplicate QIDs
            seen = set()
            deduped = []

            for c in candidates:
                qid = c.get("id")
                if not qid or qid in seen:
                    continue
                seen.add(qid)
                deduped.append(c)

            # always allow creation option
            deduped.append({
                "id": "__create__",
                "label": label
            })

            output.append({
                "id": local_id,
                "name": label,
                "bucket": bucket_name,
                "type": "entity",
                "candidates": deduped
            })

    print(f"[export] done: {len(output)} rows", flush=True)

    return output