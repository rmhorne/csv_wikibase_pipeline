# cache.py
import json
from pathlib import Path

def load_cache(path):
    p = Path(path)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"_counter": 1000, "levels": {}}

def save_cache(cache, path):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")
