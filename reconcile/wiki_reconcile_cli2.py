import json
import requests
import csv
import argparse


# =========================================================
# CONFIG
# =========================================================
CONFIG_PATH = "reconcile/wiki_config.json"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_csv(path):
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def print_block(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def pretty(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def init_log(path):
    f = open(path, "w", encoding="utf-8", newline="")
    writer = csv.DictWriter(
        f,
        fieldnames=["local_id", "label", "candidate_id", "status", "error"]
    )
    writer.writeheader()
    return f, writer


# =========================================================
# SAFE QID VALIDATION
# =========================================================
def validate_qid(session, api_url, qid):
    r = session.get(api_url, params={
        "action": "wbgetentities",
        "ids": qid,
        "format": "json"
    })

    data = r.json()

    if "entities" not in data or qid not in data["entities"]:
        raise ValueError(f"Invalid QID: {qid}")

    return True


# =========================================================
# CSRF
# =========================================================
def get_csrf(session, api_url):
    r = session.get(api_url, params={
        "action": "query",
        "meta": "tokens",
        "type": "csrf",
        "format": "json"
    })
    return r.json()["query"]["tokens"]["csrftoken"]


# =========================================================
# LOGIN
# =========================================================
def mediawiki_login(session, api_url, username, password):

    r1 = session.get(api_url, params={
        "action": "query",
        "meta": "tokens",
        "type": "login",
        "format": "json"
    })

    token = r1.json()["query"]["tokens"]["logintoken"]

    r2 = session.post(api_url, data={
        "action": "login",
        "lgname": username,
        "lgpassword": password,
        "lgtoken": token,
        "format": "json"
    })

    result = r2.json()["login"]["result"]
    print("[login]", result)

    return result == "Success"


# =========================================================
# USERINFO (FIXED)
# =========================================================
def probe_userinfo(session, api_url, label):
    print_block(f"[STEP] USERINFO ({label})")

    r = session.get(api_url, params={
        "action": "query",
        "meta": "userinfo",
        "uiprop": "groups|rights",
        "format": "json"
    })

    pretty(r.json())
    return r.json()


# =========================================================
# IDEMPOTENT ENTITY CREATION
# =========================================================
def create_entity_if_needed(session, api_url, label):
    """
    Prevent duplicate creation by first searching for existing label.
    """

    # SEARCH FIRST (prevents duplicates)
    search = session.get(api_url, params={
        "action": "wbsearchentities",
        "search": label,
        "language": "en",
        "format": "json"
    }).json()

    if search.get("search"):
        best = search["search"][0]
        return best["id"], False  # existing

    # CREATE NEW
    csrf = get_csrf(session, api_url)

    r = session.post(api_url, data={
        "action": "wbeditentity",
        "format": "json",
        "new": "item",
        "token": csrf,
        "data": json.dumps({
            "labels": {
                "en": {
                    "language": "en",
                    "value": label
                }
            }
        })
    })

    data = r.json()

    if "error" in data:
        raise RuntimeError(data["error"])

    return data["entity"]["id"], True


# =========================================================
# RECONCILIATION ENGINE
# =========================================================
def run_reconciliation(session, api_url, input_csv, log_path):

    print_block("[STEP 6] RECONCILIATION EXECUTION")

    rows = load_csv(input_csv)

    log_file, log_writer = init_log(log_path)

    result_map = {}

    stats = {
        "total": 0,
        "mapped": 0,
        "created": 0,
        "errors": 0,
        "skipped": 0
    }

    for row in rows:

        stats["total"] += 1

        local_id = row.get("id")
        label = row.get("candidate_label") or row.get("query")
        candidate_id = row.get("candidate_id")
        wiki_match = str(row.get("wiki_match", "")).strip().lower()

        if not local_id:
            stats["skipped"] += 1
            continue

        try:

            # =================================================
            # ACCEPT EXISTING
            # =================================================
            if wiki_match in ("y", "yes", "true", "1") and candidate_id and candidate_id.startswith("Q"):

                validate_qid(session, api_url, candidate_id)

                result_map[local_id] = {
                    "qid": candidate_id,
                    "created": False
                }

                stats["mapped"] += 1

                log_writer.writerow({
                    "local_id": local_id,
                    "label": label,
                    "candidate_id": candidate_id,
                    "status": "mapped",
                    "error": ""
                })
                continue

            # =================================================
            # CREATE / REUSE
            # =================================================
            if candidate_id == "__create__":

                qid, created = create_entity_if_needed(session, api_url, label)

                result_map[local_id] = {
                    "qid": qid,
                    "created": created
                }

                stats["created"] += int(created)

                log_writer.writerow({
                    "local_id": local_id,
                    "label": label,
                    "candidate_id": "__create__",
                    "status": "created" if created else "reused",
                    "error": ""
                })
                continue

            raise ValueError(f"Unresolved row: {row}")

        except Exception as e:

            stats["errors"] += 1

            log_writer.writerow({
                "local_id": local_id,
                "label": label,
                "candidate_id": candidate_id,
                "status": "error",
                "error": str(e)
            })

    log_file.close()

    return result_map, stats


# =========================================================
# MAIN
# =========================================================
def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--log", required=True)

    args = parser.parse_args()

    cfg = load_config()
    api = cfg["api_url"]

    session = requests.Session()

    # auth
    apache = cfg.get("apache_auth", {})
    if apache.get("enabled"):
        session.auth = (apache["username"], apache["password"])

    # basic checks
    probe_userinfo(session, api, "BEFORE LOGIN")

    bot = cfg.get("wikibase_bot_auth", {})
    if bot.get("enabled"):
        mediawiki_login(session, api, bot["username"], bot["password"])

    probe_userinfo(session, api, "AFTER LOGIN")

    # reconcile
    result_map, stats = run_reconciliation(
        session,
        api,
        args.input,
        args.log
    )

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result_map, f, indent=2, ensure_ascii=False)

    print_block("[DONE]")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()