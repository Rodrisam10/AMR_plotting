#!/usr/bin/env python3
import argparse
from ete3 import Tree


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract leaf order from rooted tree")
    parser.add_argument("--tree", required=True)
    parser.add_argument("--outgroup", default="Reference")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    t = Tree(args.tree, format=1, quoted_node_names=True)
    leaves = {leaf.name for leaf in t.iter_leaves()}
    if args.outgroup in leaves:
        t.set_outgroup(args.outgroup)

    with open(args.out, "w", encoding="utf-8") as out:
        for leaf in t.iter_leaves():
            if leaf.name == args.outgroup:
                continue
            out.write(f"{leaf.name}\n")

    print(f"Leaf order written to {args.out}")


if __name__ == "__main__":
    main()
