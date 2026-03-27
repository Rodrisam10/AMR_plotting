# Troubleshooting

## `['Reference'] not in index`

`Reference` esta en el arbol pero no en matriz AMR. El plotting filtra por interseccion de muestras.

## Todo `SUSC` en `mdr_labels.tsv`

Verifica que AMRFinder tenga columna `Gene symbol` y que el parseo use esa columna.

## Error de memoria/disco durante `fasterq-dump`

- Reduce `THREADS`.
- Usa `CLEANUP_LEVEL=light` o `aggressive`.
- Monitorea con `bash scripts/storage_report.sh outputs`.

## Arbol no soporta outgroup

Si `OUTGROUP_NAME` no existe, el script conserva el enraizamiento original.
