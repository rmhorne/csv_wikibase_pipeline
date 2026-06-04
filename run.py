#run.py
import argparse
from ingest import run


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--file", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--mode", choices=["dry", "simulate", "commit"], default="dry")

    args = parser.parse_args()

    run(
        file_path=args.file,
        config_path=args.config,
        mode=args.mode
    )


if __name__ == "__main__":
    main()