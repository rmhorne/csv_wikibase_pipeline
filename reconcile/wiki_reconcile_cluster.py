import re
from collections import defaultdict
from difflib import SequenceMatcher


def normalize(text: str) -> str:
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[()\-:,]", "", text)
    return text


def similarity(a: str, b: str) -> float:
    a = normalize(a)
    b = normalize(b)

    if not a or not b:
        return 0.0

    if a == b:
        return 1.0

    if a in b or b in a:
        return 0.92

    return SequenceMatcher(None, a, b).ratio()


class CanonicalClusterer:
    """
    Turns flat candidate lists into latent entity clusters.
    This is what OpenRefine actually wants conceptually.
    """

    def __init__(self, threshold: float = 0.82):
        self.threshold = threshold

    def cluster(self, candidates):
        """
        Input:
            [
              {id, label, score, source},
              ...
            ]

        Output:
            [
              {
                "cluster_id": "C0",
                "canonical_label": "...",
                "best_score": 0.93,
                "members": [...]
              }
            ]
        """

        clusters = []

        for cand in candidates:
            placed = False

            for cluster in clusters:
                rep = cluster["canonical_label"]

                if similarity(rep, cand.get("label")) >= self.threshold:
                    cluster["members"].append(cand)
                    cluster["best_score"] = max(cluster["best_score"], cand.get("score", 0.0))
                    placed = True
                    break

            if not placed:
                clusters.append({
                    "cluster_id": f"C{len(clusters)}",
                    "canonical_label": cand.get("label"),
                    "best_score": cand.get("score", 0.0),
                    "members": [cand]
                })

        # sort clusters by strength
        clusters.sort(key=lambda c: c["best_score"], reverse=True)

        return clusters