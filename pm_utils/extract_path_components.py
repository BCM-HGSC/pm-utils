import sys
import argparse
from pathlib import Path


def run(file_path, components):
    with open(file_path, "r") as file:
        for line in file:
            filepath = line.strip()
            path = Path(filepath)
            filename = path.name
            filestem = path.with_suffix("").stem
            grandparent = (
                path.parent.parent.name
                if path.parent.parent
                else ""
            )
            parent = path.parent.name
            results = []
            for c in components:
                if c ==  "n":
                    results.append(filename)
                elif c == "s":
                    results.append(filestem)
                elif c == "g":
                    results.append(grandparent)
                elif c == "d":
                    results.append(parent)
                elif c == "p":
                    results.append(filepath)
            print("\t".join(results))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Split file paths into components"
    )
    parser.add_argument(
        "components",
        metavar="component",
        type=str,
        help="Components to include in output: n (filename), s (filestem), g (grandparent), d (parent), p (filepath)",
    )
    parser.add_argument(
        "file",
        metavar="file",
        type=str,
        help="Input file containing file paths",
    )

    args = parser.parse_args()
    components = args.components

    if set(components) - {"n", "s", "g", "d", "p"}:
        print(
            "Invalid components. Please use only 'n', 's', 'g', 'd', 'p'."
        )
        sys.exit(1)

    return args



def main():
    args = parse_args()
    run(args.file, args.components)

if __name__ == "__main__":
    main()
