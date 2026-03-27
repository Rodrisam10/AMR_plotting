#!/usr/bin/env python3
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import gridspec


CLASS_COLLAPSE = {
    "CARBAPENEM": "CARBAPENEM",
    "CARBAPENEM;BETA-LACTAM": "CARBAPENEM",
    "BETA-LACTAM": "BETA-LACTAM",
    "CEPHALOSPORIN": "BETA-LACTAM",
    "BETA-LACTAM;CEPHALOSPORIN": "BETA-LACTAM",
    "MONOBACTAM": "BETA-LACTAM",
    "QUINOLONE": "QUINOLONE",
    "FLUOROQUINOLONE": "QUINOLONE",
    "AMINOGLYCOSIDE": "AMINOGLYCOSIDE",
    "TETRACYCLINE": "TETRACYCLINE",
    "PHENICOL": "PHENICOL",
    "FOSFOMYCIN": "FOSFOMYCIN",
    "TRIMETHOPRIM": "TRIMETHOPRIM",
}

CLASS_COLORS = {
    "CARBAPENEM": "#d73027",
    "BETA-LACTAM": "#fc8d59",
    "QUINOLONE": "#4575b4",
    "AMINOGLYCOSIDE": "#1a9850",
    "TETRACYCLINE": "#91bfdb",
    "PHENICOL": "#e0f3f8",
    "FOSFOMYCIN": "#fdae61",
    "TRIMETHOPRIM": "#d9ef8b",
    "OTHER": "lightgray",
}


def collapse_class(raw: str) -> str:
    value = (raw or "").strip()
    return CLASS_COLLAPSE.get(value, "OTHER")


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot AMR dot profile with class brackets")
    parser.add_argument("--leaf-order", required=True)
    parser.add_argument("--amr-matrix", required=True)
    parser.add_argument("--gene-classes", required=True)
    parser.add_argument("--out-png", required=True)
    parser.add_argument("--out-svg", required=True)
    args = parser.parse_args()

    leaf_order = [l.strip() for l in open(args.leaf_order, encoding="utf-8") if l.strip()]

    df = pd.read_csv(args.amr_matrix, sep="\t", dtype=str).set_index("strain")
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    common_strains = [s for s in leaf_order if s in df.index]
    df = df.loc[common_strains]

    gene_classes_raw = {}
    gdf = pd.read_csv(args.gene_classes, sep="\t", dtype=str)
    for _, r in gdf.iterrows():
        gene_classes_raw[str(r["gene"]).strip()] = collapse_class(str(r["class"]).strip())

    genes = [g for g in df.columns if g in gene_classes_raw]
    df = df[genes]

    classes_order = [
        "CARBAPENEM",
        "BETA-LACTAM",
        "QUINOLONE",
        "AMINOGLYCOSIDE",
        "TETRACYCLINE",
        "PHENICOL",
        "FOSFOMYCIN",
        "TRIMETHOPRIM",
        "OTHER",
    ]

    genes_with_cls = [(g, gene_classes_raw[g]) for g in df.columns]
    genes_with_cls.sort(
        key=lambda x: (classes_order.index(x[1]) if x[1] in classes_order else len(classes_order), x[0])
    )
    ordered_genes = [g for g, _ in genes_with_cls]
    ordered_classes = [c for _, c in genes_with_cls]
    df = df[ordered_genes]

    n_strains, n_genes = df.shape

    fig = plt.figure(figsize=(20, 10))
    gs = gridspec.GridSpec(2, 1, height_ratios=[0.7, 3], hspace=0.02)
    ax_top = fig.add_subplot(gs[0])
    ax_heat = fig.add_subplot(gs[1])

    ax_top.set_xlim(-0.5, n_genes - 0.5)
    ax_top.set_ylim(0, 1)
    ax_top.axis("off")

    brackets = []
    if ordered_classes:
        start = 0
        current_cls = ordered_classes[0]
        for i, cls in enumerate(ordered_classes[1:], start=1):
            if cls != current_cls:
                brackets.append((start, i - 1, current_cls))
                start = i
                current_cls = cls
        brackets.append((start, n_genes - 1, current_cls))

    for start, end, cls in brackets:
        x0 = start - 0.5
        x1 = end + 0.5
        y = 0.72
        ax_top.plot([x0, x1], [y, y], color="black", linewidth=1.2)
        ax_top.text((x0 + x1) / 2, 0.38, cls, ha="center", va="bottom", fontsize=7)

    ax_heat.set_xlim(-0.5, n_genes - 0.5)
    ax_heat.set_ylim(n_strains - 0.5, -0.5)

    for i, strain in enumerate(df.index):
        for j, gene in enumerate(df.columns):
            if int(df.iloc[i, j]) == 0:
                continue
            cls = gene_classes_raw.get(gene, "OTHER")
            ax_heat.scatter(j, i, s=40, color=CLASS_COLORS.get(cls, "lightgray"), edgecolor="k", linewidth=0.2)

    for start, _, _ in brackets:
        ax_heat.axvline(x=start - 0.5, color="black", linewidth=0.6, linestyle="--", alpha=0.7)
    if brackets:
        ax_heat.axvline(x=brackets[-1][1] + 0.5, color="black", linewidth=0.6, linestyle="--", alpha=0.7)

    ax_heat.set_xticks(range(n_genes))
    ax_heat.set_xticklabels(df.columns, rotation=90, fontsize=6)
    ax_heat.set_yticks(range(n_strains))
    ax_heat.set_yticklabels(df.index, fontsize=6)
    ax_heat.set_xlabel("Genes de resistencia", fontsize=10)
    ax_heat.set_ylabel("Muestras", fontsize=10)

    plt.subplots_adjust(left=0.15, right=0.98, top=0.95, bottom=0.22)
    plt.savefig(args.out_png, dpi=300)
    plt.savefig(args.out_svg)
    print(f"Wrote {args.out_png}")
    print(f"Wrote {args.out_svg}")


if __name__ == "__main__":
    main()
