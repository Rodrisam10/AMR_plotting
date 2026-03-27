#!/usr/bin/env python3
import argparse
from ete3 import Tree, TreeStyle, AttrFace


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot rectangular phylogenetic tree with ETE3")
    parser.add_argument("--tree", required=True)
    parser.add_argument("--outgroup", default="Reference")
    parser.add_argument("--out-png", required=True)
    parser.add_argument("--out-svg", required=True)
    args = parser.parse_args()

    t = Tree(args.tree, format=1, quoted_node_names=True)
    leaves = {leaf.name for leaf in t.iter_leaves()}
    if args.outgroup in leaves:
        t.set_outgroup(args.outgroup)

    ts = TreeStyle()
    ts.mode = "r"
    ts.show_leaf_name = False
    ts.scale = 50
    ts.min_leaf_separation = 12
    ts.show_scale = True

    for leaf in t.iter_leaves():
        leaf.add_face(AttrFace("name", fsize=7), column=0, position="aligned")

    t.render(args.out_png, w=2000, units="px", dpi=300, tree_style=ts)
    t.render(args.out_svg, w=2000, units="px", dpi=300, tree_style=ts)
    print(f"Wrote {args.out_png}")
    print(f"Wrote {args.out_svg}")


if __name__ == "__main__":
    main()
