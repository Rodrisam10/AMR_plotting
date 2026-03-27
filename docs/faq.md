# FAQ

## Por que usar SRA crudo y no ensamblados directos?

Para mayor resolucion SNP y menos sesgo por diferencias de ensamblado.

## Snippy requiere FASTQ?

Puede usar `--ctgs`, pero para este proyecto se prioriza `--R1/--R2`.

## Puedo correr solo una parte del pipeline?

Si. Los scripts de `scripts/` son modulares y pueden ejecutarse por etapa.

## Como evitar mismatch filogenia-resistoma?

Usar `sample_id` canonico desde `samples.tsv` en todas las etapas.
