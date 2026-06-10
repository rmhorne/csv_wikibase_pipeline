import requests
from utils import write_json


class WikibaseEntityCreator:
    """
    ONLY responsible for:
    - creating missing entities
    - returning QIDs
    """

    def __init__(self, api_url, auth=None):
        self.api_url = api_url
        self.session = requests.Session()

        if auth:
            self.session.auth = auth

    def create_item(self, label):
        payload = {
            "action": "wbeditentity",
            "format": "json",
            "new": "item",
            "data": {
                "labels": {
                    "en": {
                        "language": "en",
                        "value": label
                    }
                }
            }
        }

        r = self.session.post(self.api_url, json=payload)
        data = r.json()

        return data["entity"]["id"]


def create_missing_entities(alignment_map, labels_lookup, api_url, auth=None):
    """
    alignment_map:
        QW1009 -> "__create__" or "Q123"

    labels_lookup:
        QW1009 -> "Adon Olam"
    """

    creator = WikibaseEntityCreator(api_url, auth)

    final_map = {}

    print("[stage4] creating missing entities...")

    for local_id, qid in alignment_map.items():

        if qid != "__create__":
            final_map[local_id] = qid
            continue

        label = labels_lookup.get(local_id)

        if not label:
            print(f"[stage4] SKIP missing label: {local_id}")
            continue

        new_qid = creator.create_item(label)

        print(f"[stage4] {local_id} -> {new_qid}")

        final_map[local_id] = new_qid

    return final_map


def write_complete_alignment(mapping, out_path):
    write_json(mapping, out_path)