import json
import csv


# =========================================================
# FLATTENER
# =========================================================
def flatten_reconcile_input(data):
    """
    Input:
    [
        {
            "id": "QW1001",
            "name": "Adon olam",
            "bucket": "expression",
            "type": "entity",
            "candidates": [...]
        }
    ]

    Output:
    One row per candidate.
    """

    rows = []

    for entry in data:

        local_id = entry.get("id")
        query = entry.get("name")
        bucket = entry.get("bucket")
        entity_type = entry.get("type")

        candidates = entry.get("candidates", [])

        for c in candidates:

            qid = c.get("id")

            if isinstance(qid, str) and qid.startswith("Q"):
                candidate_url = f"https://husky.oarc.ucla.edu/wiki/Item:{qid}"
            else:
                candidate_url = ""

            rows.append({
                "id": local_id,
                "query": query,
                "bucket": bucket,
                "entity_type": entity_type,

                "candidate_id": qid,
                "candidate_label": c.get("label"),
                "candidate_description": c.get("description"),
                "candidate_score": c.get("score"),
                "candidate_source": c.get("source"),

                "candidate_url": candidate_url,

                "wiki_match": False
            })

    return rows


# =========================================================
# CORE EXPORT
# =========================================================
def build_openrefine_export(clustered_records):
    return flatten_reconcile_input(clustered_records)


# =========================================================
# JSON EXPORT
# =========================================================
def write_openrefine_json(clustered_records, out_path):

    rows = build_openrefine_export(clustered_records)

    payload = {
        "result": rows
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(
            payload,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"[openrefine-json] wrote {len(rows)} rows → {out_path}",
        flush=True
    )


# =========================================================
# CSV EXPORT
# =========================================================
def write_openrefine_csv(clustered_records, out_path):

    rows = build_openrefine_export(clustered_records)

    if not rows:

        with open(out_path, "w", encoding="utf-8") as f:
            f.write("")

        print("[csv] no rows", flush=True)
        return

    fieldnames = [
        "id",
        "query",
        "bucket",
        "entity_type",

        "candidate_id",
        "candidate_label",
        "candidate_description",
        "candidate_score",
        "candidate_source",

        "candidate_url",

        "match"
    ]

    with open(
        out_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            extrasaction="ignore"
        )

        writer.writeheader()

        for row in rows:
            writer.writerow(row)

    print(
        f"[csv] wrote {len(rows)} rows → {out_path}",
        flush=True
    )