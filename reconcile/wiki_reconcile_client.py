import requests
import time
import re
from rapidfuzz import fuzz


class WikiReconcileClient:
    """
    SURFACE RECONCILIATION CLIENT (STABLE VERSION)

    Fixes:
    - replaces difflib with rapidfuzz (better name matching)
    - fixes A.J. vs AJ vs A J issues via token-based scoring
    - keeps API behavior unchanged
    """

    # =========================================================
    # INIT
    # =========================================================
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

        self._status = {}
        self._probe_all()

    # =========================================================
    # STATUS PROBES (unchanged)
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
                params={
                    "action": "query",
                    "meta": "userinfo",
                    "format": "json"
                },
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
                params={
                    "action": "query",
                    "meta": "tokens",
                    "type": "csrf",
                    "format": "json"
                },
                timeout=10
            )
            r.raise_for_status()

            token = r.json().get("query", {}).get("tokens", {}).get("csrftoken")
            self._status["csrf_ok"] = bool(token)

            print("[status] CSRF OK" if token else "[status] CSRF MISSING", flush=True)

        except Exception as e:
            self._status["csrf_ok"] = False
            self._status["csrf_error"] = str(e)

    # =========================================================
    # NORMALIZATION (SIMPLIFIED ON PURPOSE)
    # We DO NOT over-engineer this anymore.
    # rapidfuzz handles structure differences.
    # =========================================================
    def _normalize(self, s: str) -> str:
        if not s:
            return ""

        s = str(s).lower().strip()
        s = re.sub(r"\s+", " ", s)

        # IMPORTANT:
        # we only lightly remove punctuation spacing artifacts
        # NOT aggressive collapsing (that caused AJ vs A J bugs)
        s = re.sub(r"[^\w\s\.]", "", s)

        return s

    # =========================================================
    # SCORE (REPLACED WITH RAPIDFUZZ)
    # =========================================================
    def _score(self, q, c):
        if not q or not c:
            return 0.0

        qn = self._normalize(q)
        cn = self._normalize(c)

        # Exact match
        if qn == cn:
            return 1.0

        # Token-aware match (VERY IMPORTANT FIX)
        return fuzz.token_set_ratio(qn, cn) / 100.0

    # =========================================================
    # LOCAL SURFACE
    # =========================================================
    def _local(self, label):
        return [{
            "id": None,
            "label": label,
            "score": 0.98,
            "source": "local"
        }]

    # =========================================================
    # VARIANTS (kept but simplified)
    # =========================================================
    def _variants(self, label):
        base = self._normalize(label)
        tokens = base.split()

        variants = set()
        variants.add(label)
        variants.add(base)

        for t in tokens:
            variants.add(t)

        if len(tokens) > 1:
            variants.add(" ".join(reversed(tokens)))

        return list(variants)

    # =========================================================
    # WIKIBASE SEARCH
    # =========================================================
    def _wikibase(self, label, limit=10):
        results = []

        queries = [label] + self._variants(label)

        for q in queries:
            try:
                print(f"[wikibase] query: {q}", flush=True)

                t0 = time.time()
                r = self.session.get(
                    self.api_url,
                    params={
                        "action": "wbsearchentities",
                        "search": q,
                        "format": "json",
                        "language": "en",
                        "limit": limit
                    },
                    timeout=15
                )
                dt = time.time() - t0

                r.raise_for_status()

                data = r.json().get("search", [])
                print(f"[wikibase] response_time={dt:.3f}s results={len(data)}", flush=True)

                for x in data:
                    results.append({
                        "id": x.get("id"),
                        "label": x.get("label"),
                        "description": x.get("description"),
                        "score": self._score(label, x.get("label", "")),
                        "source": "wikibase"
                    })

            except Exception as e:
                print(f"[wikibase] error: {e}", flush=True)
                continue

        return results

    # =========================================================
    # MAIN SEARCH API
    # =========================================================
    def search(self, label, limit=15):
        print("\n[surface] ==============================", flush=True)
        print(f"[surface] QUERY: {label}", flush=True)

        candidates = []

        candidates.extend(self._local(label))
        candidates.extend(self._wikibase(label, limit=limit))

        candidates.append({
            "id": "__create__",
            "label": label,
            "score": 0.0,
            "source": "create"
        })

        candidates.sort(key=lambda x: x.get("score", 0), reverse=True)

        final = candidates[:limit + 10]

        print(f"[surface] returned={len(final)}", flush=True)

        for i, c in enumerate(final[:12], 1):
            print(
                f"[surface] {i}. {c.get('label')} "
                f"(score={c.get('score'):.2f}, source={c.get('source')})",
                flush=True
            )

        return final