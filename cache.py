from pathlib import Path
from utils import load_json, write_json


def load_cache(path: Path):
    path = Path(path)

    if path.exists():
        cache = load_json(path)
    else:
        cache = {}

    cache.setdefault("_counter", 1000)
    cache.setdefault("levels", {})

    return cache


def save_cache(cache, path: Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(cache, path)