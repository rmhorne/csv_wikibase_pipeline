import requests
import time
from difflib import SequenceMatcher

from wiki_reconcile_cluster import CanonicalClusterer


class WikiReconcileClient:
    """
    SURFACE RECONCILIATION LAYER (OpenRefine-style)
    - returns clustered fuzzy candidates
    - preserves ambiguity
    - never collapses to single truth
    """

    def __init__(self, config):
        self.api_url = config["api_url"]
        self.session = requests.Session()

        apache = config.get("apache_auth", {})
        if apache.get("enabled"):
            self.session.auth = (
                apache["username"],
                apache["password"]
            )

        print("[init] Wikibase Surface Client", flush=True)
        print(f"[init] endpoint: {self.api_url}", flush=True)

        self.clusterer = CanonicalClusterer(threshold=0.80)
        self._status = {}

        self._probe_all()

    # =========================================================
    # STATUS (unchanged)
    # =========================================================
    def _probe_all(self):
        print("[status] probing system...", flush=True)
        self._probe_http()
        self._probe_userinfo()
        self._probe_search()
        self._probe_csrf()

        print("[status] ---- SUMMARY ----", flush=True)
        for k, v in self._status.items():
            print(f"[status] {k}: {v}", flush=True)

    def _probe_http(self):
        try:
            t0 = time.time()
            r = self.session.get(self.api_url, timeout=10)
            dt = time.time() - t0

            self._status["http_ok"] = True
            self._status["http_ms"] = round(dt * 1000, 2)
            self._status["http_code"] = r.status_code

            print(f"[status] HTTP OK ({r.status_code}) {dt:.2f}s", flush=True)

        except Exception as e:
            self._status["http_ok"] = False
            self._status["http_error"] = str(e)
            raise

    def _probe_userinfo(self):
        try:
            r = self.session.get(
                self.api_url,
                params={"action": "query", "meta": "userinfo", "format": "json"},
                timeout=10
            )
            r.raise_for_status()

            ui = r.json().get("query", {}).get("userinfo", {})
            name = ui.get("name")

            self._status["user"] = name
            self._status["anon"] = not bool(name)

            print(f"[status] AUTH user = {name}", flush=True)

        except Exception as e:
            self._status["auth_error"] = str(e)

    def _probe_search(self):
        try:
            r = self.session.get(
                self.api_url,
                params={
                    "action": "wbsearchentities",
                    "search": "test",
                    "format": "json",
                    "language": "en",
                    "limit": 1
                },
                timeout=10
            )
            r.raise_for_status()

            data = r.json().get("search", [])
            self._status["search_ok"] = True
            self._status["search_results"] = len(data)

            print(f"[status] SEARCH OK ({len(data)})", flush=True)

        except Exception as e:
            self._status["search_ok"] = False
            self._status["search_error"] = str(e)

    def _probe_csrf(self):
        try:
            r = self.session.get(
                self.api_url,
                params={"action": "query", "meta": "tokens", "type": "csrf", "format": "json"},
                timeout=10
            )
            r.raise_for_status()

            token = r.json().get("query", {}).get("tokens", {}).get("csrftoken")
            self._status["csrf_ok"] = bool(token)

            print("[status] CSRF OK" if token else "[status] CSRF missing", flush=True)

        except Exception as e:
            self._status["csrf_ok"] = False
            self._status["csrf_error"] = str(e)

    # =========================================================
    # CORE SEARCH (RAW)
    # =========================================================
    def _wikibase_search(self, label, limit=10):
        try:
            r = self.session.get(
                self.api_url,
                params={
                    "action": "wbsearchentities",
                    "search": label,
                    "format": "json",
                    "language": "en",
                    "limit": limit
                },
                timeout=15
            )
            r.raise_for_status()

            data = r.json().get("search", [])

            results = []
            for x in data:
                results.append({
                    "id": x.get("id"),
                    "label": x.get("label"),
                    "description": x.get("description"),
                    "score": SequenceMatcher(None, label.lower(), (x.get("label") or "").lower()).ratio(),
                    "source": "wikibase"
                })

            return results

        except Exception:
            return []

    # =========================================================
    # SURFACE SEARCH (MAIN API)
    # =========================================================
    def search(self, label, limit=10):
        print(f"\n[surface] QUERY: {label}", flush=True)

        candidates = []

        # raw wikibase
        wb = self._wikibase_search(label, limit=limit * 2)
        candidates.extend(wb)

        # always include create option
        candidates.append({
            "id": "__create__",
            "label": label,
            "score": 0.0,
            "source": "create"
        })

        # cluster fuzzy duplicates
        clusters = self.clusterer.cluster(candidates)

        # flatten clusters into OpenRefine-friendly output
        output = []

        for c in clusters:
            for m in c["members"]:
                output.append({
                    "cluster_id": c["cluster_id"],
                    "canonical_label": c["canonical_label"],
                    "id": m.get("id"),
                    "label": m.get("label"),
                    "description": m.get("description"),
                    "score": m.get("score"),
                    "cluster_score": c["best_score"],
                    "source": m.get("source"),
                    "match_type": "fuzzy_cluster"
                })

        # sort final output
        output.sort(key=lambda x: x["cluster_score"], reverse=True)

        print(f"[surface] returned={len(output)}")
        for i, o in enumerate(output[:12], 1):
            print(
                f"[surface] {i}. {o['label']} "
                f"(score={o['score']:.2f}, cluster={o['cluster_id']}, source={o['source']})"
            )

        return output