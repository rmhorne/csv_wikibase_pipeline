import json
import requests


def create_entity(session, api_url, label):
    """
    Create Wikibase entity safely (no imports, no cycles).
    """

    # CSRF token
    r1 = session.get(api_url, params={
        "action": "query",
        "meta": "tokens",
        "type": "csrf",
        "format": "json"
    })

    token = r1.json()["query"]["tokens"]["csrftoken"]

    # create entity
    r2 = session.post(api_url, data={
        "action": "wbeditentity",
        "format": "json",
        "new": "item",
        "token": token,
        "data": json.dumps({
            "labels": {
                "en": {
                    "language": "en",
                    "value": label
                }
            }
        })
    })

    data = r2.json()

    if "error" in data:
        raise RuntimeError(data["error"])

    return data["entity"]["id"]