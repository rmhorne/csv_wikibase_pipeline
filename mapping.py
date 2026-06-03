from utils import normalize_text


def make_work_key(row, key_columns):
    if not key_columns:
        return None

    values = []
    for col in key_columns:
        values.append(normalize_text(row.get(col), allow_empty=True) or "")

    return "|".join(values)
