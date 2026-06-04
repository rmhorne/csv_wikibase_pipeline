import json
import re
from pathlib import Path


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(data, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def normalize(x):
    if x is None:
        return None

    x = str(x).strip()
    x = re.sub(r"\s+", " ", x)

    if x.lower() in {"nan", "none", "null", ""}:
        return None

    return x


def key(x):
    x = normalize(x)
    if x is None:
        return None
    return x.lower()