# Flowchart detallado

Este diagrama resume el pipeline completo con componentes, scripts, entradas y salidas.

```mermaid
flowchart TD
  A0[Run pipeline script\nrun_prjna717739_pipeline.sh + prjna717739.env] --> A1[Validate config and create output folders]

  A1 --> B1[Download RunInfo CSV\nOutput: outputs metadata runinfo]
  B1 --> B2[parse_runinfo.py\nFilter: Illumina + PAIRED\nOutput: outputs metadata samples.tsv]

  B2 --> C0{For each sample_id in samples.tsv}

  C0 --> C1[prefetch\nInput: run ID\nOutput: outputs sra run.sra]
  C1 --> C2[fasterq-dump + gzip\nOutput: outputs fastq R1 R2 gz]
  C2 --> C3[fastp\nOutput: outputs fastp R1 R2 gz + QC logs]

  C3 --> C4[snippy R1 R2\nOutput: outputs snippy sample snps.vcf snps.tab snps.aligned.fa]
  C3 --> C5[shovill\nOutput: outputs assembly sample contigs.fa]
  C5 --> C6[amrfinder\nOutput: outputs amr sample_amr.tsv]

  C2 --> CL1{Cleanup level}
  CL1 -->|light or aggressive| CL2[Delete SRA files]
  CL1 -->|aggressive| CL3[Delete raw FASTQ files]
  C6 --> CL4{Cleanup level}
  CL4 -->|aggressive| CL5[Delete fastp FASTQ files]

  C4 --> C0
  C6 --> C0

  C0 -->|Loop finished| D1[snippy-core\nOutput: outputs core core.full.aln core.aln core.tab]
  D1 --> D2[snp-sites\nOutput: outputs core core.snp.fasta]
  D2 --> D3[iqtree2\nOutput: outputs tree kp_snps.treefile and kp_snps.contree]

  C6 --> E1[build_gene_classes.py\nOutput: outputs amr gene_classes.tsv]
  C6 --> E2[build_amr_matrix.py\nOutput: outputs amr amr_matrix.tsv and mdr_labels.tsv]
  D3 --> E3[get_leaf_order.py\nOutput: outputs tree leaf_order.txt]

  D3 --> F1[plot_tree_rectangular.py\nOutput: outputs figures kp_tree_rectangular png svg]
  E1 --> F2[plot_amr_profile.py]
  E2 --> F2
  E3 --> F2
  F2 --> F3[Output: outputs figures amr_profile_dots png svg]

  F1 --> G1[storage_report.sh\nOutput: per-folder disk usage]
  F3 --> G1
  G1 --> G2[Final artifacts\nTree contree, AMR matrix, gene classes, figures]
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
