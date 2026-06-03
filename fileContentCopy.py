from pathlib import Path

def dump_python_project(root_dir: str, output_file: str = "output.txt"):
    root = Path(root_dir)

    with open(output_file, "w", encoding="utf-8") as out:

        out.write(f"PYTHON PROJECT DUMP\nROOT: {root.resolve()}\n\n")

        for path in sorted(root.rglob("*")):
            if path.is_dir():
                continue

            rel_path = path.relative_to(root)

            # Print directory structure line
            out.write(f"\nFILE: {rel_path}\n")
            out.write("-" * 80 + "\n")

            # Only dump python files fully
            if path.suffix == ".py":
                try:
                    content = path.read_text(encoding="utf-8")
                except Exception as e:
                    content = f"[ERROR READING FILE: {e}]"

                out.write(content)
                out.write("\n")
            else:
                out.write("[non-python file skipped]\n")

        out.write("\nDONE\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python dump.py /path/to/project")
    else:
        dump_python_project(sys.argv[1])