# cli.py

import argparse

from triples import run
from utils import write_json


def main():
    p = argparse.ArgumentParser()

    p.add_argument("--csv", required=True)
    p.add_argument("--config", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--cache", required=True)

    args = p.parse_args()

    plan = run(
        csv_path=args.csv,
        config_path=args.config,
        cache_path=args.cache
    )

    print(f"\nSTATEMENTS: {len(plan)}")

    write_json(plan, args.out)


if __name__ == "__main__":
    main()