import argparse
from pathlib import Path
from ingest import run
from utils import write_json


def main():
    p = argparse.ArgumentParser()

    p.add_argument("--csv", required=True)
    p.add_argument("--config", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--cache", required=True)
    p.add_argument("--mode", default="dry")

    args = p.parse_args()

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.cache).parent.mkdir(parents=True, exist_ok=True)

    plan = run(args.csv, args.config, args.cache)

    if args.mode == "dry":
        write_json([s.__dict__ for s in plan], args.out)

    print(f"OK: {len(plan)} statements")


if __name__ == "__main__":
    main()