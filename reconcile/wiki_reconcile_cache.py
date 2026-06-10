import json
from pathlib import Path


def load_cache(path):
    path = Path(path)

    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))

    return {
        "_counter": 1000,
        "levels": {
            "entity": {}
        }
    }


def save_cache(cache, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cache, indent=2), encoding="utf-8")