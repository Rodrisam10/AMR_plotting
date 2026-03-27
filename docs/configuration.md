# Configuracion

El pipeline se controla con `config/prjna717739.env`.

Variables principales:

- `BIOPROJECT_ID`: BioProject de entrada.
- `REFERENCE_FASTA`: referencia genómica usada por Snippy.
- `OUTDIR`: carpeta de resultados.
- `THREADS`: hilos por etapa.
- `CLEANUP_LEVEL`: `none`, `light` o `aggressive`.
- `OUTGROUP_NAME`: nombre de outgroup para el arbol.

Ejemplo:

```bash
BIOPROJECT_ID=PRJNA717739
OUTDIR=./outputs
THREADS=8
REFERENCE_FASTA=./reference/k_pneumoniae_MGH78578_ref.fna
CLEANUP_LEVEL=light
OUTGROUP_NAME=Reference
PREFETCH_MAX_SIZE=100G
```
