# AMRplotting (PRJNA717739 test)

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![Lifecycle: experimental](https://img.shields.io/badge/lifecycle-experimental-orange.svg)](https://lifecycle.r-lib.org/articles/stages.html#experimental)
[![BioProject: PRJNA717739](https://img.shields.io/badge/BioProject-PRJNA717739-blue.svg)](https://www.ncbi.nlm.nih.gov/bioproject/PRJNA717739)
[![Python 3.10](https://img.shields.io/badge/python-3.10-3776AB?logo=python&logoColor=white)](./environment.yml)
[![NGS Input: SRA paired-end](https://img.shields.io/badge/NGS-SRA%20paired--end-6f42c1.svg)](#)

Pipeline reproducible para filogenomica de resistencia en *Klebsiella pneumoniae* usando lecturas crudas SRA paired-end (Illumina).

Objetivo:
- Estimar SNPs con Snippy desde FASTQ crudo para mejor resolucion.
- Inferir arbol filogenetico robusto.
- Extraer resistoma con AMRFinderPlus.
- Integrar filogenia + AMR sin desalineacion de muestras.
- Controlar cuellos de botella de almacenamiento y depurar intermedios no criticos.

## 1) Estructura del proyecto

```text
.
├─ README.md
├─ environment.yml
├─ config/
│  └─ prjna717739.env
├─ scripts/
│  ├─ run_prjna717739_pipeline.sh
│  ├─ parse_runinfo.py
│  ├─ get_leaf_order.py
│  ├─ build_gene_classes.py
│  ├─ build_amr_matrix.py
│  ├─ plot_tree_rectangular.py
│  ├─ plot_amr_profile.py
│  └─ storage_report.sh
└─ outputs/
   ├─ logs/
   ├─ metadata/
   ├─ sra/
   ├─ fastq/
   ├─ fastp/
   ├─ snippy/
   ├─ core/
   ├─ tree/
   ├─ assembly/
   ├─ amr/
   └─ figures/
```

## 2) Requisitos

Crear entorno:

```bash
mamba env create -f environment.yml
mamba activate amrplot
```

## 3) Configuracion minima

Editar `config/prjna717739.env`:

- `BIOPROJECT_ID=PRJNA717739`
- `REFERENCE_FASTA=/ruta/a/referencia.fna`
- `OUTDIR=./outputs`
- `THREADS=8`
- `CLEANUP_LEVEL=light` (`none|light|aggressive`)
- `OUTGROUP_NAME=Reference` (si aplica)

Nota: el pipeline asume datos paired-end Illumina (filtrados desde SRA RunInfo).

## 4) Ejecucion end-to-end

```bash
bash scripts/run_prjna717739_pipeline.sh config/prjna717739.env
```

## 5) Flujo de trabajo (facil)

1. Descargar RunInfo del BioProject.
2. Filtrar a Illumina + PAIRED y construir `samples.tsv` (llave canonica = `sample_id`).
3. `prefetch` + `fasterq-dump` para obtener FASTQ.
4. `fastp` para limpieza.
5. `snippy --R1/--R2` por muestra.
6. `snippy-core` + `snp-sites`.
7. `iqtree2` para arbol.
8. Ensamblado para AMR (`shovill`) + `amrfinder`.
9. Matriz de genes AMR + perfil por clases.
10. Figuras finales:
   - arbol rectangular
   - dot-plot AMR con brackets por clase.

## 6) Cuellos de botella de almacenamiento

Este pipeline es intensivo en disco. Regla practica para paired-end:

- `.sra`: 1x
- `fasterq-dump` FASTQ descomprimido: 4x-8x
- FASTQ gz: 2x-3x
- intermedios de ensamblado + snippy: 1x-2x

Ejemplo orientativo para 100 GB en SRA:
- Pico sin limpieza: 600-900 GB
- Pico con `CLEANUP_LEVEL=light`: 300-500 GB
- Pico con `CLEANUP_LEVEL=aggressive`: 180-300 GB

### Politica de depuracion

- `none`: conserva todo.
- `light`: borra `.sra` cuando FASTQ y logs estan correctos.
- `aggressive`: ademas borra FASTQ crudo tras generar `fastp` y borra FASTQ `fastp` tras terminar Snippy + ensamblado + AMR para esa muestra.

Siempre se conservan:
- `outputs/metadata/samples.tsv`
- `outputs/snippy/*/snps.vcf`
- `outputs/snippy/*/snps.tab`
- `outputs/snippy/*/snps.aligned.fa`
- `outputs/core/*`
- `outputs/tree/*`
- `outputs/amr/*_amr.tsv`
- `outputs/figures/*`

Generar reporte de disco:

```bash
bash scripts/storage_report.sh outputs
```

## 7) Reproducibilidad (clave para evitar mismatch filogenia-resistoma)

Todo se integra por `sample_id` en `outputs/metadata/samples.tsv`.

Columnas minimas:
- `sample_id`
- `run`
- `library_layout`
- `platform`
- `fastq_r1`
- `fastq_r2`
- `snippy_dir`
- `assembly_fasta`
- `amr_tsv`

Si un sample no existe en algun modulo, se reporta en log y no se mezcla de forma silenciosa.

## 8) Scripts de analisis y figuras

1) Orden de hojas del arbol:

```bash
python scripts/get_leaf_order.py \
  --tree outputs/tree/kp_snps.contree \
  --outgroup "$OUTGROUP_NAME" \
  --out outputs/tree/leaf_order.txt
```

2) Construir clases de genes desde AMRFinder:

```bash
python scripts/build_gene_classes.py \
  --amr-dir outputs/amr \
  --out outputs/amr/gene_classes.tsv
```

3) Matriz AMR binaria:

```bash
python scripts/build_amr_matrix.py \
  --amr-dir outputs/amr \
  --samples outputs/metadata/samples.tsv \
  --out-matrix outputs/amr/amr_matrix.tsv \
  --out-labels outputs/amr/mdr_labels.tsv
```

4) Arbol rectangular:

```bash
python scripts/plot_tree_rectangular.py \
  --tree outputs/tree/kp_snps.contree \
  --outgroup "$OUTGROUP_NAME" \
  --out-png outputs/figures/kp_tree_rectangular.png \
  --out-svg outputs/figures/kp_tree_rectangular.svg
```

5) Perfil AMR (dot-plot con brackets y separadores):

```bash
python scripts/plot_amr_profile.py \
  --leaf-order outputs/tree/leaf_order.txt \
  --amr-matrix outputs/amr/amr_matrix.tsv \
  --gene-classes outputs/amr/gene_classes.tsv \
  --out-png outputs/figures/amr_profile_dots.png \
  --out-svg outputs/figures/amr_profile_dots.svg
```

## 9) Troubleshooting rapido

- Error `['Reference'] not in index` en plotting:
  - `Reference` esta en el arbol pero no en matriz AMR. El script ya filtra por interseccion.
- Arbol con nodos internos fusionados en web/json:
  - usar IDs internos unicos (si exportas a Cytoscape).
- Todo `SUSC` en `mdr_labels.tsv`:
  - revisar parseo de columna de `Gene symbol` (AMRFinder).

## 10) Resultado minimo esperado

- `outputs/tree/kp_snps.contree`
- `outputs/amr/amr_matrix.tsv`
- `outputs/amr/gene_classes.tsv`
- `outputs/figures/kp_tree_rectangular.png`
- `outputs/figures/amr_profile_dots.png`

Con esto tienes version filogenomica de resistencia reproducible y trazable.

## 11) License

CC BY-NC-SA 4.0. Ver `LICENSE.md`.
