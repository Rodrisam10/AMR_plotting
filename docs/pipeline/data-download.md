# Descarga de datos (SRA/BioProject)

El pipeline usa RunInfo de NCBI y filtra automaticamente a corridas validas (`ILLUMINA` + `PAIRED`).

Comandos relevantes:

```bash
curl -L "https://trace.ncbi.nlm.nih.gov/Traces/study/?acc=PRJNA717739&rettype=runinfo&display=csv" -o outputs/metadata/runinfo_PRJNA717739.csv
python scripts/parse_runinfo.py --runinfo outputs/metadata/runinfo_PRJNA717739.csv --out outputs/metadata/samples.tsv
```

Luego, por cada `run`:

```bash
prefetch <RUN> --max-size 100G --output-directory outputs/sra
fasterq-dump <RUN> -e 8 -O outputs/fastq
gzip -f outputs/fastq/<RUN>_1.fastq
gzip -f outputs/fastq/<RUN>_2.fastq
```
