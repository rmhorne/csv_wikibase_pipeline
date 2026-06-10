from utils import load_json, write_json
import csv
from pathlib import Path


def load_alignment_csv(path):
    """
    alignment.csv format:

    id,query,bucket,entity_type,candidate_id,...,wiki_match
    """

    mapping = {}

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            local_id = row["id"]
            qid = row["candidate_id"]
            match = row.get("wiki_match") or row.get("match")

            if not local_id:
                continue

            # Stage 4 rule:
            # only accept explicit positive match OR __create__
            if qid == "__create__":
                mapping[local_id] = "__create__"
                continue

            if match and str(match).lower() in {"y", "yes", "true", "1"}:
                if qid and qid.startswith("Q"):
                    mapping[local_id] = qid

    return mapping


def write_alignment_json(mapping, out_path):
    write_json(mapping, out_path)