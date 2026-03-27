# Instalacion

## Requisitos

- mamba o conda
- git
- acceso a internet para SRA y NCBI

## Entorno

```bash
mamba env create -f environment.yml
mamba activate amrplot
```

## Dependencias de documentacion (opcional)

```bash
pip install -r requirements-docs.txt
```

## Verificar comandos clave

```bash
snippy --version
iqtree2 --version
amrfinder -h
prefetch --help
```
