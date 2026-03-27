#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build paired-end Illumina sample manifest from SRA RunInfo CSV")
    parser.add_argument("--runinfo", required=True, help="Path to runinfo CSV")
    parser.add_argument("--out", required=True, help="Output samples.tsv")
    args = parser.parse_args()

    in_path = Path(args.runinfo)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows_out = []

    with in_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            run = (row.get("Run") or "").strip()
            platform = (row.get("Platform") or "").strip().upper()
            layout = (row.get("LibraryLayout") or "").strip().upper()

            if not run:
                continue
            if platform != "ILLUMINA":
                continue
            if layout != "PAIRED":
                continue

            sample_id = run
            rows_out.append(
                {
                    "sample_id": sample_id,
                    "run": run,
                    "platform": platform,
                    "layout": layout,
                }
            )

    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["sample_id", "run", "platform", "layout"], delimiter="\t")
        w.writeheader()
        for r in rows_out:
            w.writerow(r)

    print(f"Wrote {len(rows_out)} paired-end Illumina runs to {out_path}")


if __name__ == "__main__":
    main()
