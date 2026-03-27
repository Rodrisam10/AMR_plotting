# Estructura de outputs

`outputs/` se organiza por etapa:

- `metadata/`: runinfo y manifest (`samples.tsv`).
- `sra/`: archivos `.sra`.
- `fastq/`: FASTQ crudo.
- `fastp/`: FASTQ filtrado.
- `snippy/`: resultados por muestra.
- `core/`: core alignment y SNP alignment.
- `tree/`: arboles (`.treefile`, `.contree`) y orden de hojas.
- `assembly/`: ensamblados para AMR.
- `amr/`: resultados AMRFinder y matrices.
- `figures/`: figuras finales.
- `logs/`: logs de pipeline y fastp.
