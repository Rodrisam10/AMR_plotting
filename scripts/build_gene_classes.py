#!/usr/bin/env python3
import argparse
from pathlib import Path
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description="Build gene->class table from AMRFinder TSV files")
    parser.add_argument("--amr-dir", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    amr_dir = Path(args.amr_dir)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    gene_to_class = {}
    files = sorted(amr_dir.glob("*_amr.tsv"))

    for f in files:
        try:
            df = pd.read_csv(f, sep="\t", dtype=str)
        except Exception:
            continue

        if "Gene symbol" not in df.columns:
            continue

        for _, row in df.iterrows():
            gene = str(row.get("Gene symbol", "")).strip()
            if not gene:
                continue

            cls = str(row.get("Class", "")).strip()
            if not cls:
                cls = str(row.get("Element subtype", "")).strip() or str(row.get("Element type", "")).strip() or "OTHER"

            if gene not in gene_to_class:
                gene_to_class[gene] = cls

    out_df = pd.DataFrame(sorted(gene_to_class.items()), columns=["gene", "class"])
    out_df.to_csv(out, sep="\t", index=False)
    print(f"Wrote {len(out_df)} genes to {out}")


if __name__ == "__main__":
    main()
