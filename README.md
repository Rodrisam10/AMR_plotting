# AMRplotting

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![Lifecycle: experimental](https://img.shields.io/badge/lifecycle-experimental-orange.svg)](https://lifecycle.r-lib.org/articles/stages.html#experimental)
[![BioProject: PRJNA717739](https://img.shields.io/badge/BioProject-PRJNA717739-blue.svg)](https://www.ncbi.nlm.nih.gov/bioproject/PRJNA717739)
[![Python 3.10](https://img.shields.io/badge/python-3.10-3776AB?logo=python&logoColor=white)](./environment.yml)
[![NGS Input: SRA paired-end](https://img.shields.io/badge/NGS-SRA%20paired--end-6f42c1.svg)](#)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-0A66C2)](https://rodrisam10.github.io/AMR_plotting/)

## Developed by

Elías Romero

- Author's name: Elías Romero
- ORCID: [0009-0005-0375-8145](https://orcid.org/0009-0005-0375-8145)

## English

AMRplotting is a reproducible phylogenomics pipeline for *Klebsiella pneumoniae* antimicrobial resistance analysis from raw SRA paired-end Illumina reads.

### Main goals

- Call SNPs with Snippy from raw FASTQ for improved resolution.
- Infer robust phylogenetic trees.
- Build AMR profiles with AMRFinderPlus.
- Integrate phylogeny + resistome with consistent sample matching.
- Control storage bottlenecks and remove non-critical intermediates.

### Quick start

```bash
mamba env create -f environment.yml
mamba activate amrplot
bash scripts/run_prjna717739_pipeline.sh config/prjna717739.env
```

### Core structure

```text
.
├─ config/
├─ scripts/
├─ docs/
├─ outputs/
├─ environment.yml
└─ README.md
```

### Key outputs

- `outputs/tree/kp_snps.contree`
- `outputs/amr/amr_matrix.tsv`
- `outputs/amr/gene_classes.tsv`
- `outputs/figures/kp_tree_rectangular.png`
- `outputs/figures/amr_profile_dots.png`

### Full documentation

- https://rodrisam10.github.io/AMR_plotting/



## Espanol

AMRplotting es un pipeline reproducible de filogenomica para analizar resistencia antimicrobiana en *Klebsiella pneumoniae* a partir de lecturas crudas SRA paired-end Illumina.

### Objetivos principales

- Estimar SNPs con Snippy desde FASTQ crudo para mejor resolucion.
- Inferir arboles filogeneticos robustos.
- Construir perfiles de resistencia con AMRFinderPlus.
- Integrar filogenia + resistoma con match consistente de muestras.
- Controlar cuellos de botella de almacenamiento y depurar intermedios no criticos.

### Inicio rapido

```bash
mamba env create -f environment.yml
mamba activate amrplot
bash scripts/run_prjna717739_pipeline.sh config/prjna717739.env
```

### Estructura base

```text
.
├─ config/
├─ scripts/
├─ docs/
├─ outputs/
├─ environment.yml
└─ README.md
```

### Salidas clave

- `outputs/tree/kp_snps.contree`
- `outputs/amr/amr_matrix.tsv`
- `outputs/amr/gene_classes.tsv`
- `outputs/figures/kp_tree_rectangular.png`
- `outputs/figures/amr_profile_dots.png`

### Documentacion completa

- https://rodrisam10.github.io/AMR_plotting/

## License

CC BY-NC-SA 4.0. See `LICENSE.md`.
