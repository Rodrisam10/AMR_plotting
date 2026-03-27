# Resumen del flujo

Pipeline principal:

1. RunInfo del BioProject.
2. Filtro a Illumina paired-end.
3. Descarga SRA + conversion a FASTQ.
4. QC con fastp.
5. SNP calling con Snippy (R1/R2).
6. Core SNP alignment con snippy-core y snp-sites.
7. Arbol con IQ-TREE2.
8. Ensamblado para AMR y AMRFinderPlus.
9. Matriz AMR + figuras finales.

Ejecucion completa:

```bash
bash scripts/run_prjna717739_pipeline.sh config/prjna717739.env
```
