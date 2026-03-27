# Almacenamiento y limpieza

Este pipeline puede crecer rapido en disco, principalmente por `fasterq-dump`.

## Estimacion orientativa (paired-end)

- SRA: 1x
- FASTQ descomprimido: 4x-8x
- FASTQ gz: 2x-3x
- intermedios snippy+assembly: 1x-2x

## Politica de limpieza

- `none`: conserva todo.
- `light`: elimina `.sra` tras generar FASTQ y logs.
- `aggressive`: elimina tambien FASTQ intermedios cuando ya no son necesarios.

Reporte rapido:

```bash
bash scripts/storage_report.sh outputs
```
