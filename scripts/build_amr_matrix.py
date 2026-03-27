#!/usr/bin/env python3
import argparse
import csv
import re
from pathlib import Path
import pandas as pd


ESBL_PATTERNS = [r"blaSHV", r"blaCTX", r"blaCTX-M", r"blaTEM", r"blaOXA-1"]
CARB_PATTERNS = [r"blaKPC", r"blaNDM", r"blaOXA-48", r"blaOXA-181", r"blaVIM", r"blaIMP"]
FQ_PATTERNS = [r"qnr", r"oqxA", r"oqxB"]
TET_PATTERNS = [r"tet"]
PHENICOL_PATTERNS = [r"catA", r"floR"]
FOS_PATTERNS = [r"fos"]


def matches_any(gene: str, patterns: list[str]) -> bool:
    return any(re.search(p, gene) for p in patterns)


def classify(genes: list[str]) -> str:
    flags = []
    if any(matches_any(g, CARB_PATTERNS) for g in genes):
        flags.append("CARB")
    if any(matches_any(g, ESBL_PATTERNS) for g in genes):
        flags.append("ESBL")
    if any(matches_any(g, FQ_PATTERNS) for g in genes):
        flags.append("FQ")

    classes_count = 0
    for patterns in [ESBL_PATTERNS, CARB_PATTERNS, FQ_PATTERNS, TET_PATTERNS, PHENICOL_PATTERNS, FOS_PATTERNS]:
        if any(matches_any(g, patterns) for g in genes):
            classes_count += 1
    if classes_count >= 3:
        flags.append("MDR")

    if not flags:
        flags = ["SUSC"]
    return ",".join(flags)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build AMR binary matrix and simplified MDR labels")
    parser.add_argument("--amr-dir", required=True)
    parser.add_argument("--samples", required=True)
    parser.add_argument("--out-matrix", required=True)
    parser.add_argument("--out-labels", required=True)
    args = parser.parse_args()

    amr_dir = Path(args.amr_dir)
    out_matrix = Path(args.out_matrix)
    out_labels = Path(args.out_labels)
    out_matrix.parent.mkdir(parents=True, exist_ok=True)

    samples_df = pd.read_csv(args.samples, sep="\t", dtype=str)
    samples = samples_df["sample_id"].tolist()

    sample_to_genes = {s: set() for s in samples}
    all_genes = set()

    for sample_id in samples:
        f = amr_dir / f"{sample_id}_amr.tsv"
        if not f.exists():
            continue
        try:
            df = pd.read_csv(f, sep="\t", dtype=str)
        except Exception:
            continue
        if "Gene symbol" not in df.columns:
            continue

        genes = [str(g).strip() for g in df["Gene symbol"].dropna().tolist() if str(g).strip()]
        sample_to_genes[sample_id] = set(genes)
        all_genes.update(genes)

    all_genes_sorted = sorted(all_genes)

    with out_matrix.open("w", encoding="utf-8", newline="") as out:
        w = csv.writer(out, delimiter="\t")
        w.writerow(["strain"] + all_genes_sorted)
        for s in samples:
            row = [s] + [1 if g in sample_to_genes[s] else 0 for g in all_genes_sorted]
            w.writerow(row)

    with out_labels.open("w", encoding="utf-8", newline="") as out:
        w = csv.writer(out, delimiter="\t")
        w.writerow(["accession", "mdr_category"])
        for s in samples:
            genes = sorted(sample_to_genes[s])
            w.writerow([s, classify(genes)])

    print(f"Wrote matrix: {out_matrix}")
    print(f"Wrote labels: {out_labels}")


if __name__ == "__main__":
    main()
