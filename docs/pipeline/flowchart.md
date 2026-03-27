# Flowchart detallado

Este diagrama resume el pipeline completo con componentes, scripts, entradas y salidas.

```mermaid
flowchart TD
  %% =========================
  %% CONFIG / SETUP
  %% =========================
  A0[Usuario ejecuta\n`bash scripts/run_prjna717739_pipeline.sh config/prjna717739.env`] --> A1[config/prjna717739.env\nBIOPROJECT_ID, REFERENCE_FASTA, OUTDIR, THREADS, CLEANUP_LEVEL]
  A1 --> A2[Crear arbol de salidas\noutputs/{logs,metadata,sra,fastq,fastp,snippy,core,tree,assembly,amr,figures}]

  %% =========================
  %% METADATA / MANIFEST
  %% =========================
  A2 --> B1[curl RunInfo CSV\nInput: BIOPROJECT_ID\nOutput: outputs/metadata/runinfo_<ID>.csv]
  B1 --> B2[`python scripts/parse_runinfo.py`\nInput: runinfo CSV\nFiltro: ILLUMINA + PAIRED\nOutput: outputs/metadata/samples.tsv]

  %% =========================
  %% PER-SAMPLE PROCESSING
  %% =========================
  B2 --> C0{Loop por sample_id en\nsamples.tsv}

  C0 --> C1[prefetch\nInput: run\nOutput: outputs/sra/<run>.sra]
  C1 --> C2[fasterq-dump + gzip\nInput: .sra\nOutput: outputs/fastq/<run>_1.fastq.gz\noutputs/fastq/<run>_2.fastq.gz]
  C2 --> C3[fastp\nInput: FASTQ crudo\nOutput: outputs/fastp/<sample>_R1.fastq.gz\noutputs/fastp/<sample>_R2.fastq.gz\nlogs HTML/JSON]

  C3 --> C4[snippy --R1/--R2\nInput: fastp FASTQ + REFERENCE_FASTA\nOutput: outputs/snippy/<sample>/snps.vcf\noutputs/snippy/<sample>/snps.tab\noutputs/snippy/<sample>/snps.aligned.fa]

  C3 --> C5[shovill\nInput: fastp FASTQ\nOutput: outputs/assembly/<sample>/contigs.fa]
  C5 --> C6[amrfinder\nInput: contigs.fa\nOutput: outputs/amr/<sample>_amr.tsv]

  %% cleanup decisions
  C2 --> CL1{CLEANUP_LEVEL}
  CL1 -->|light/aggressive| CL2[Eliminar outputs/sra/<run>.sra]
  CL1 -->|aggressive| CL3[Eliminar FASTQ crudo\noutputs/fastq/*]
  C6 --> CL4{CLEANUP_LEVEL}
  CL4 -->|aggressive| CL5[Eliminar FASTQ de fastp\noutputs/fastp/<sample>_R1/R2.fastq.gz]

  C4 --> C0
  C6 --> C0

  %% =========================
  %% CORE SNP + TREE
  %% =========================
  C0 -->|fin loop| D1[snippy-core\nInput: outputs/snippy/* + REFERENCE_FASTA\nOutput: outputs/core/core.full.aln\noutputs/core/core.aln\noutputs/core/core.tab]
  D1 --> D2[snp-sites\nInput: core.full.aln\nOutput: outputs/core/core.snp.fasta]
  D2 --> D3[iqtree2\nInput: core.snp.fasta\nOutput: outputs/tree/kp_snps.treefile\noutputs/tree/kp_snps.contree]

  %% =========================
  %% AMR TABLES / INTEGRATION
  %% =========================
  C6 --> E1[`python scripts/build_gene_classes.py`\nInput: outputs/amr/*_amr.tsv\nOutput: outputs/amr/gene_classes.tsv]
  C6 --> E2[`python scripts/build_amr_matrix.py`\nInput: outputs/amr/*_amr.tsv + samples.tsv\nOutput: outputs/amr/amr_matrix.tsv\noutputs/amr/mdr_labels.tsv]
  D3 --> E3[`python scripts/get_leaf_order.py`\nInput: kp_snps.contree\nOutput: outputs/tree/leaf_order.txt]

  %% =========================
  %% FIGURES
  %% =========================
  D3 --> F1[`python scripts/plot_tree_rectangular.py`\nInput: kp_snps.contree\nOutput: outputs/figures/kp_tree_rectangular.png/.svg]
  E2 --> F2[`python scripts/plot_amr_profile.py`]
  E1 --> F2
  E3 --> F2
  F2 --> F3[Input: leaf_order.txt + amr_matrix.tsv + gene_classes.tsv\nOutput: outputs/figures/amr_profile_dots.png/.svg]

  %% =========================
  %% REPORTING
  %% =========================
  F1 --> G1[`bash scripts/storage_report.sh outputs`\nOutput: consumo por carpeta + total]
  F3 --> G1
  G1 --> G2[Pipeline finalizado\nResultados minimos:\n- kp_snps.contree\n- amr_matrix.tsv\n- gene_classes.tsv\n- figuras PNG/SVG]
```

## Scripts y contratos (input/output)

| Script | Input principal | Output principal |
|---|---|---|
| `scripts/parse_runinfo.py` | `runinfo_<BIOPROJECT>.csv` | `samples.tsv` (solo Illumina paired-end) |
| `scripts/run_prjna717739_pipeline.sh` | `config/prjna717739.env` + utilidades CLI | Arbol completo de `outputs/` |
| `scripts/build_gene_classes.py` | `outputs/amr/*_amr.tsv` | `outputs/amr/gene_classes.tsv` |
| `scripts/build_amr_matrix.py` | `outputs/amr/*_amr.tsv` + `samples.tsv` | `amr_matrix.tsv` + `mdr_labels.tsv` |
| `scripts/get_leaf_order.py` | `kp_snps.contree` | `leaf_order.txt` |
| `scripts/plot_tree_rectangular.py` | `kp_snps.contree` | `kp_tree_rectangular.png/.svg` |
| `scripts/plot_amr_profile.py` | `leaf_order.txt`, `amr_matrix.tsv`, `gene_classes.tsv` | `amr_profile_dots.png/.svg` |
| `scripts/storage_report.sh` | `outputs/` | reporte de consumo de almacenamiento |

## Notas de trazabilidad

- La llave canonica es `sample_id` desde `samples.tsv`.
- La integracion filogenia-resistoma se hace por `sample_id` + `leaf_order.txt`.
- El cleanup nunca elimina archivos finales de analisis (arbol, matrices AMR, figuras).
