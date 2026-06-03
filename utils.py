import json
import re
from pathlib import Path

CACHE_FILE = Path("cache.json")
CONFIG_FILE = Path("config.json")
CONNECTION_FILE = Path("connection.json")


def load_json_file(path):
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def normalize_text(text, lower=False, allow_empty=False):
    """
    STRICT normalization layer:
    - handles pandas NaN
    - removes whitespace noise
    - prevents "nan" string pollution
    """

    if text is None:
        return "" if allow_empty else None

    # --- pandas NaN safety ---
    if isinstance(text, float):
        # NaN floats stringify to "nan"
        if str(text).lower() == "nan":
            return None

    text = str(text).strip()

    # collapse whitespace
    text = re.sub(r"\s+", " ", text)

    # IMPORTANT: kill NaN-like strings
    if text.lower() in {"nan", "none", "null", ""}:
        return None

    if lower:
        text = text.lower()

    if not text and not allow_empty:
        return None

    return text


def normalize_entity_label(text):
    """
    Entity normalization only.

    Examples:
        gustave cohen -> Gustave Cohen
    """

    text = normalize_text(text)

    if not text:
        return text

    return text.title()


def normalize_key(text):
    normalized = normalize_text(text, lower=True)
    return normalized


def parse_year_uncertainty(val):
    """
    Handles:
    - 1942
    - 1890s?
    - 1700s?
    """

    if not val:
        return None, False

    val = str(val).strip()

    uncertain = "?" in val

    match = re.search(r"\d{3,4}", val)
    if not match:
        return None, False

    return int(match.group()), uncertain


def write_json_file(data, filename):
    path = Path(filename)
    path.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8"
    )