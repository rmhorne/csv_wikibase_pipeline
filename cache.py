from pathlib import Path
from utils import load_json, write_json


# =====================================================
# LOAD CACHE (SAFE + DETERMINISTIC)
# =====================================================

def load_cache(path: Path):
    path = Path(path)

    if path.exists():
        cache = load_json(path)
    else:
        cache = {}

    # CORE GUARANTEES (DO NOT RELAX THESE)
    cache.setdefault("_counter", 1000)
    cache.setdefault("levels", {})

    # OPTIONAL: future-proofing (safe even if unused)
    cache.setdefault("audit", {})
    cache.setdefault("reverse_index", {})

    return cache


# =====================================================
# SAVE CACHE
# =====================================================

def save_cache(cache, path: Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(cache, path)