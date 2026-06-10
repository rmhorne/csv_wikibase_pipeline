import requests


def write_plan_to_wikibase(plan, api_url, auth=None):
    session = requests.Session()

    if auth:
        session.auth = auth

    results = []

    for i, stmt in enumerate(plan, 1):
        print(f"[writeback] {i}/{len(plan)} {stmt['predicate']}", flush=True)

        payload = {
            "action": "wbeditentity",
            "format": "json",
            "data": {
                "claims": {
                    stmt["predicate"]: [{
                        "mainsnak": {
                            "snaktype": "value",
                            "property": stmt["predicate"],
                            "datavalue": {
                                "value": stmt["object"],
                                "type": "string"
                            }
                        },
                        "type": "statement"
                    }]
                }
            }
        }

        r = session.post(api_url, json=payload)
        results.append(r.json())

    return results