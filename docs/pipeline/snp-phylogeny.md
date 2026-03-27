# SNP y filogenia

## Snippy con lecturas crudas

```bash
snippy --cpus 8 --outdir outputs/snippy/<sample_id> --ref <reference.fna> --R1 <R1.fastq.gz> --R2 <R2.fastq.gz>
```

## Core SNP

```bash
snippy-core --ref <reference.fna> --prefix outputs/core/core outputs/snippy/*
snp-sites -o outputs/core/core.snp.fasta outputs/core/core.full.aln
```

## Arbol

```bash
iqtree2 -s outputs/core/core.snp.fasta -m GTR+G -bb 1000 -nt AUTO -pre outputs/tree/kp_snps
```

Salida clave:
- `outputs/tree/kp_snps.contree`
