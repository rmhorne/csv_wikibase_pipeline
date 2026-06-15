# Quick trace script — run this instead of cli.py to see what's happening
import pandas as pd
from utils import load_json, normalize, identity_key
from cache import load_cache

csv_path    = "data/raw/milken_spotify.csv"
config_path = "config/config-v3.json"
cache_path  = "out/cache.json"

df     = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
config = load_json(config_path)
cache  = load_cache(cache_path)

print(f"CSV rows: {len(df)}")
print(f"CSV columns: {list(df.columns)}")
print()

# Show first row raw
row = df.iloc[0].to_dict()
print("=== FIRST ROW (raw) ===")
for k, v in list(row.items())[:10]:
    print(f"  {k!r}: {v!r}")
print()

# Check row identity config
row_cfg   = config.get("row", {})
id_cfg    = row_cfg.get("identity", {})
print(f"=== ROW IDENTITY CONFIG ===")
print(f"  full identity cfg: {id_cfg}")
print()

fields    = id_cfg.get("fields", [])
separator = id_cfg.get("separator", " | ")
print(f"  fields:    {fields}")
print(f"  separator: {separator!r}")
print()

# Try to build the composite key
parts = []
for f in fields:
    v = normalize(row.get(f))
    parts.append(v if v is not None else "")
    print(f"  field {f!r} -> raw={row.get(f)!r} -> normalized={v!r}")

print(f"  parts: {parts}")
print(f"  all empty: {all(p == '' for p in parts)}")
if parts:
    key = separator.join(parts)
    print(f"  composite key: {key!r}")
