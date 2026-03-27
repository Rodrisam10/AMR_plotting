#!/usr/bin/env bash
set -euo pipefail

OUTDIR="${1:-./outputs}"
if [[ ! -d "$OUTDIR" ]]; then
  echo "Directory not found: $OUTDIR"
  exit 1
fi

echo "Storage report for: $OUTDIR"
echo "----------------------------------------"
for d in metadata sra fastq fastp snippy core tree assembly amr figures logs; do
  if [[ -d "$OUTDIR/$d" ]]; then
    du -sh "$OUTDIR/$d"
  fi
done
echo "----------------------------------------"
du -sh "$OUTDIR"
