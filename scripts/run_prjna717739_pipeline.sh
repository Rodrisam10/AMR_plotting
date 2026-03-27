#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: bash scripts/run_prjna717739_pipeline.sh <config.env>"
  exit 1
fi

CONFIG_FILE="$1"
if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "Config file not found: $CONFIG_FILE"
  exit 1
fi

# shellcheck disable=SC1090
source "$CONFIG_FILE"

required_vars=(BIOPROJECT_ID OUTDIR THREADS REFERENCE_FASTA CLEANUP_LEVEL PREFETCH_MAX_SIZE)
for v in "${required_vars[@]}"; do
  if [[ -z "${!v:-}" ]]; then
    echo "Missing required config variable: $v"
    exit 1
  fi
done

if [[ ! -f "$REFERENCE_FASTA" ]]; then
  echo "Reference file not found: $REFERENCE_FASTA"
  exit 1
fi

mkdir -p "$OUTDIR"/{logs,metadata,sra,fastq,fastp,snippy,core,tree,assembly,amr,figures}

LOG_FILE="$OUTDIR/logs/pipeline_$(date +%Y%m%d_%H%M%S).log"
touch "$LOG_FILE"

log() {
  local msg="$1"
  printf '[%s] %s\n' "$(date '+%F %T')" "$msg" | tee -a "$LOG_FILE"
}

run_cmd() {
  log "CMD: $*"
  "$@" 2>&1 | tee -a "$LOG_FILE"
}

cleanup_after_fastq() {
  local run_id="$1"
  if [[ "$CLEANUP_LEVEL" == "light" || "$CLEANUP_LEVEL" == "aggressive" ]]; then
    rm -f "$OUTDIR/sra/${run_id}"*.sra || true
    log "Cleanup: removed SRA for $run_id"
  fi
}

cleanup_after_fastp() {
  local run_id="$1"
  if [[ "$CLEANUP_LEVEL" == "aggressive" ]]; then
    rm -f "$OUTDIR/fastq/${run_id}"*.fastq "$OUTDIR/fastq/${run_id}"*.fastq.gz || true
    log "Cleanup: removed raw FASTQ for $run_id"
  fi
}

cleanup_after_sample_complete() {
  local run_id="$1"
  if [[ "$CLEANUP_LEVEL" == "aggressive" ]]; then
    rm -f "$OUTDIR/fastp/${run_id}"*.fastq.gz || true
    log "Cleanup: removed fastp FASTQ for $run_id"
  fi
}

log "Step 1/8: Download BioProject RunInfo for $BIOPROJECT_ID"
RUNINFO_CSV="$OUTDIR/metadata/runinfo_${BIOPROJECT_ID}.csv"
run_cmd curl -L "https://trace.ncbi.nlm.nih.gov/Traces/study/?acc=${BIOPROJECT_ID}&rettype=runinfo&display=csv" -o "$RUNINFO_CSV"

log "Step 2/8: Build paired-end Illumina manifest"
SAMPLES_TSV="$OUTDIR/metadata/samples.tsv"
run_cmd python scripts/parse_runinfo.py --runinfo "$RUNINFO_CSV" --out "$SAMPLES_TSV"

log "Step 3/8: Per-sample download, QC, Snippy, assembly, AMR"
while IFS=$'\t' read -r sample_id run platform layout; do
  if [[ "$sample_id" == "sample_id" ]]; then
    continue
  fi

  log "Processing sample_id=$sample_id run=$run"

  run_cmd prefetch "$run" --max-size "$PREFETCH_MAX_SIZE" --output-directory "$OUTDIR/sra"

  run_cmd fasterq-dump "$run" -e "$THREADS" -O "$OUTDIR/fastq"
  run_cmd gzip -f "$OUTDIR/fastq/${run}_1.fastq"
  run_cmd gzip -f "$OUTDIR/fastq/${run}_2.fastq"
  cleanup_after_fastq "$run"

  run_cmd fastp \
    -i "$OUTDIR/fastq/${run}_1.fastq.gz" \
    -I "$OUTDIR/fastq/${run}_2.fastq.gz" \
    -o "$OUTDIR/fastp/${sample_id}_R1.fastq.gz" \
    -O "$OUTDIR/fastp/${sample_id}_R2.fastq.gz" \
    -w "$THREADS" \
    --html "$OUTDIR/logs/${sample_id}_fastp.html" \
    --json "$OUTDIR/logs/${sample_id}_fastp.json"
  cleanup_after_fastp "$run"

  run_cmd snippy \
    --cpus "$THREADS" \
    --outdir "$OUTDIR/snippy/${sample_id}" \
    --ref "$REFERENCE_FASTA" \
    --R1 "$OUTDIR/fastp/${sample_id}_R1.fastq.gz" \
    --R2 "$OUTDIR/fastp/${sample_id}_R2.fastq.gz"

  run_cmd shovill \
    --R1 "$OUTDIR/fastp/${sample_id}_R1.fastq.gz" \
    --R2 "$OUTDIR/fastp/${sample_id}_R2.fastq.gz" \
    --outdir "$OUTDIR/assembly/${sample_id}" \
    --cpus "$THREADS" \
    --force

  run_cmd amrfinder \
    -n "$OUTDIR/assembly/${sample_id}/contigs.fa" \
    -o "$OUTDIR/amr/${sample_id}_amr.tsv"

  cleanup_after_sample_complete "$run"

done < "$SAMPLES_TSV"

log "Step 4/8: Core SNP alignment"
run_cmd snippy-core --ref "$REFERENCE_FASTA" --prefix "$OUTDIR/core/core" "$OUTDIR/snippy"/*

log "Step 5/8: SNP-only alignment"
run_cmd snp-sites -o "$OUTDIR/core/core.snp.fasta" "$OUTDIR/core/core.full.aln"

log "Step 6/8: Tree inference with IQ-TREE2"
run_cmd iqtree2 -s "$OUTDIR/core/core.snp.fasta" -m GTR+G -bb 1000 -nt AUTO -pre "$OUTDIR/tree/kp_snps"

log "Step 7/8: AMR integration tables"
run_cmd python scripts/build_gene_classes.py --amr-dir "$OUTDIR/amr" --out "$OUTDIR/amr/gene_classes.tsv"
run_cmd python scripts/build_amr_matrix.py --amr-dir "$OUTDIR/amr" --samples "$SAMPLES_TSV" --out-matrix "$OUTDIR/amr/amr_matrix.tsv" --out-labels "$OUTDIR/amr/mdr_labels.tsv"

OUTGROUP_SAFE="${OUTGROUP_NAME:-}"
if [[ -z "$OUTGROUP_SAFE" ]]; then
  OUTGROUP_SAFE="Reference"
fi
run_cmd python scripts/get_leaf_order.py --tree "$OUTDIR/tree/kp_snps.contree" --outgroup "$OUTGROUP_SAFE" --out "$OUTDIR/tree/leaf_order.txt"

log "Step 8/8: Figures"
run_cmd python scripts/plot_tree_rectangular.py --tree "$OUTDIR/tree/kp_snps.contree" --outgroup "$OUTGROUP_SAFE" --out-png "$OUTDIR/figures/kp_tree_rectangular.png" --out-svg "$OUTDIR/figures/kp_tree_rectangular.svg"
run_cmd python scripts/plot_amr_profile.py --leaf-order "$OUTDIR/tree/leaf_order.txt" --amr-matrix "$OUTDIR/amr/amr_matrix.tsv" --gene-classes "$OUTDIR/amr/gene_classes.tsv" --out-png "$OUTDIR/figures/amr_profile_dots.png" --out-svg "$OUTDIR/figures/amr_profile_dots.svg"

log "Pipeline completed successfully"
run_cmd bash scripts/storage_report.sh "$OUTDIR"
