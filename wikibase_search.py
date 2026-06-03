import requests
from requests.auth import HTTPBasicAuth
import time

from utils import CONNECTION_FILE, load_json_file, normalize_text


def load_connection_config():
    return load_json_file(CONNECTION_FILE)


def normalize(text):
    return normalize_text(text, lower=True, allow_empty=True)


def get_session():
    config = load_connection_config()

    session = requests.Session()
    api_url = config["api_url"]

    apache = config.get("apache_auth", {})
    if apache.get("enabled"):
        session.auth = HTTPBasicAuth(apache["username"], apache["password"])

    wikibase = config.get("wikibase_auth", {})
    if wikibase.get("enabled"):
        r = session.get(
            api_url,
            params={
                "action": "query",
                "meta": "tokens",
                "type": "login",
                "format": "json"
            },
            timeout=15
        )

        try:
            token = r.json()["query"]["tokens"]["logintoken"]
        except Exception:
            print("❌ Failed to get login token")
            print(r.text[:300])
            raise

        r2 = session.post(
            api_url,
            data={
                "action": "login",
                "lgname": wikibase["username"],
                "lgpassword": wikibase["password"],
                "lgtoken": token,
                "format": "json"
            },
            timeout=15
        )

        try:
            if r2.json().get("login", {}).get("result") != "Success":
                print("❌ Wikibase login failed:")
                print(r2.json())
        except Exception:
            print("❌ Wikibase login response not JSON")
            print(r2.text[:300])
            raise

    return session


def search_entity(session, label, field_type="entity"):
    if not label:
        return []

    config = load_connection_config()
    api_url = config["api_url"]

    print(f"[SEARCH:{field_type}] {label}", flush=True)
    start = time.time()

    try:
        r = session.get(
            api_url,
            params={
                "action": "wbsearchentities",
                "search": label,
                "language": "en",
                "format": "json"
            },
            timeout=10
        )

        dt = round(time.time() - start, 2)
        print(f"[DONE:{field_type}] {label} ({dt}s status={r.status_code})", flush=True)

        try:
            data = r.json()
        except Exception:
            print(f"❌ Non-JSON response for: {label}")
            print(r.text[:300])
            return []

        matches = data.get("search", [])

        norm_label = normalize(label)
        filtered = []
        for m in matches:
            candidate = normalize(m.get("label", ""))
            if candidate == norm_label:
                filtered.append(m)

        return {
            "raw": matches,
            "filtered": filtered
        }
    except Exception as e:
        dt = round(time.time() - start, 2)
        print(f"❌ ERROR [{label}] after {dt}s: {e}", flush=True)
        return {
            "raw": [],
            "filtered": []
        }
