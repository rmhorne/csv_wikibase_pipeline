from pathlib import Path
import argparse


def dump_project(root_dir: str, output_file: str):
    root = Path(root_dir).resolve()
    out_path = Path(output_file).resolve()

    py_files = sorted(root.rglob("*.py"))

    with out_path.open("w", encoding="utf-8") as out:

        out.write(f"# PYTHON PROJECT DUMP\n")
        out.write(f"# ROOT: {root}\n")
        out.write(f"# FILE COUNT: {len(py_files)}\n\n")

        for file_path in py_files:
            # skip venv and cache dirs
            if any(part in {"venv", ".venv", "__pycache__"} for part in file_path.parts):
                continue

            rel_path = file_path.relative_to(root)

            out.write("\n" + "=" * 120 + "\n")
            out.write(f"# FILE: {rel_path}\n")
            out.write("=" * 120 + "\n\n")

            try:
                content = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                content = file_path.read_text(encoding="latin-1")

            out.write(content)
            out.write("\n")

    print(f"\n✔ Dump complete → {out_path}")
    print(f"✔ Files included: {len(py_files)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Project root directory")
    parser.add_argument("--out", default="project_dump.txt", help="Output file")

    args = parser.parse_args()

    dump_project(args.root, args.out)