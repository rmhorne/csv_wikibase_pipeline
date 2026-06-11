import json
import requests
import time


# =========================================================
# CONFIG
# =========================================================
CONFIG_PATH = "reconcile/wiki_config.json"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def print_block(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def pretty(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False))


# =========================================================
# STEP 1: APACHE GATE CHECK (NOT IDENTITY)
# =========================================================
def apache_gate_check(session, api_url):
    print_block("[STEP 1] APACHE GATE CHECK (transport only)")

    r = session.get(api_url, params={
        "action": "query",
        "format": "json"
    })

    print("[apache] HTTP status:", r.status_code)
    print("[apache] response snippet:")
    print(r.text[:300])

    return r.status_code


# =========================================================
# STEP 2: USERINFO (BEFORE LOGIN STATE)
# =========================================================
def probe_userinfo(session, api_url, label):
    print_block(f"[STEP 2] USERINFO ({label})")

    r = session.get(api_url, params={
        "action": "query",
        "meta": "userinfo",
        "uiprop": "groups|rights|name|id",
        "format": "json"
    })

    print("[userinfo raw]:")
    pretty(r.json())

    ui = r.json().get("query", {}).get("userinfo", {})

    print("\n--- PARSED ---")
    print("name  :", ui.get("name"))
    print("id    :", ui.get("id"))
    print("anon  :", ui.get("anon"))
    print("groups:", ui.get("groups"))
    print("rights:", ui.get("rights"))

    return ui


# =========================================================
# STEP 3: CSRF CHECK (NO LOGIN REQUIRED)
# =========================================================
def probe_csrf(session, api_url):
    print_block("[STEP 3] CSRF TOKEN CHECK")

    r = session.get(api_url, params={
        "action": "query",
        "meta": "tokens",
        "type": "csrf",
        "format": "json"
    })

    data = r.json()
    pretty(data)

    token = data.get("query", {}).get("tokens", {}).get("csrftoken")

    print("\nCSRF TOKEN PRESENT:", bool(token))
    print("CSRF TOKEN VALUE  :", token)

    return token


# =========================================================
# STEP 4: BOT LOGIN (EXPLICIT TRACE)
# =========================================================
def mediawiki_login(session, api_url, username, password):

    print_block("[STEP 4] MEDIAWIKI LOGIN ATTEMPT")

    print("[login] identity being used:")
    print("USERNAME:", username)
    print("PASSWORD:", "***HIDDEN***")

    # STEP 4.1 token
    r1 = session.get(api_url, params={
        "action": "query",
        "meta": "tokens",
        "type": "login",
        "format": "json"
    })

    print("\n[login] token response:")
    pretty(r1.json())

    token = r1.json().get("query", {}).get("tokens", {}).get("logintoken")

    print("[login] extracted token:", token)

    # STEP 4.2 login request
    r2 = session.post(api_url, data={
        "action": "login",
        "lgname": username,
        "lgpassword": password,
        "lgtoken": token,
        "format": "json"
    })

    print("\n[login] raw response:")
    pretty(r2.json())

    result = r2.json().get("login", {}).get("result")

    print("\n[login] RESULT STATE:", result)

    if result != "Success":
        print("\n❌ LOGIN FAILED — NO SESSION CHANGE")
        return False

    print("\n✔ LOGIN SUCCESS — SESSION SHOULD CHANGE")
    return True


# =========================================================
# STEP 5: POST-LOGIN VERIFICATION
# =========================================================
def post_login_probe(session, api_url):
    print_block("[STEP 5] POST-LOGIN IDENTITY CHECK")

    ui = probe_userinfo(session, api_url, "AFTER LOGIN")

    return ui


# =========================================================
# STEP 6: WRITE PERMISSION CHECK (REAL TEST)
# =========================================================
def probe_write_permission(session, api_url):
    print_block("[STEP 6] WRITE PERMISSION CHECK (CSRF + wbeditentity dry run)")

    csrf = probe_csrf(session, api_url)

    if not csrf:
        print("❌ NO CSRF → NO WRITE CAPABILITY")
        return

    payload = {
        "action": "wbeditentity",
        "format": "json",
        "new": "item",
        "token": csrf,
        "data": json.dumps({
            "labels": {
                "en": {
                    "language": "en",
                    "value": "AUTH_TEST_ENTITY"
                }
            }
        })
    }

    r = session.post(api_url, data=payload)

    print("\n[write test raw response]:")
    pretty(r.json())

    if "error" in r.json():
        print("\n❌ WRITE FAILED (AUTH OR PERMISSION ISSUE)")
    else:
        print("\n✔ WRITE POSSIBLE (AUTH FULLY VALIDATED)")


# =========================================================
# MAIN TRACE
# =========================================================
def main():

    print_block("[INIT] MEDIAWIKI FULL AUTH TRACE START")

    cfg = load_config()
    api = cfg["api_url"]

    session = requests.Session()

    # -----------------------------
    # Apache gate only
    # -----------------------------
    apache = cfg.get("apache_auth", {})
    if apache.get("enabled"):
        print("[apache] applying auth (transport only)")
        session.auth = (apache["username"], apache["password"])

    # -----------------------------
    # STEP 1: raw access
    # -----------------------------
    apache_gate_check(session, api)

    # -----------------------------
    # STEP 2: baseline identity
    # -----------------------------
    probe_userinfo(session, api, "BEFORE LOGIN")

    # -----------------------------
    # STEP 3: csrf baseline
    # -----------------------------
    probe_csrf(session, api)

    # -----------------------------
    # STEP 4: login
    # -----------------------------
    bot = cfg.get("wikibase_bot_auth", {})
    success = False

    if bot.get("enabled"):
        success = mediawiki_login(
            session,
            api,
            bot["username"],
            bot["password"]
        )

    # -----------------------------
    # STEP 5: post login identity
    # -----------------------------
    if success:
        post_login_probe(session, api)
    else:
        print("\n❌ SKIPPING POST LOGIN (LOGIN FAILED)")

    # -----------------------------
    # STEP 6: write capability
    # -----------------------------
    probe_write_permission(session, api)


if __name__ == "__main__":
    main()