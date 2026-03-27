# Resistoma e integracion filogenomica

## AMR por muestra

```bash
shovill --R1 <R1.fastq.gz> --R2 <R2.fastq.gz> --outdir outputs/assembly/<sample_id> --cpus 8 --force
amrfinder -n outputs/assembly/<sample_id>/contigs.fa -o outputs/amr/<sample_id>_amr.tsv
```

## Integracion

```bash
python scripts/build_gene_classes.py --amr-dir outputs/amr --out outputs/amr/gene_classes.tsv
python scripts/build_amr_matrix.py --amr-dir outputs/amr --samples outputs/metadata/samples.tsv --out-matrix outputs/amr/amr_matrix.tsv --out-labels outputs/amr/mdr_labels.tsv
python scripts/get_leaf_order.py --tree outputs/tree/kp_snps.contree --outgroup Reference --out outputs/tree/leaf_order.txt
```

## Figuras

```bash
python scripts/plot_tree_rectangular.py --tree outputs/tree/kp_snps.contree --outgroup Reference --out-png outputs/figures/kp_tree_rectangular.png --out-svg outputs/figures/kp_tree_rectangular.svg
python scripts/plot_amr_profile.py --leaf-order outputs/tree/leaf_order.txt --amr-matrix outputs/amr/amr_matrix.tsv --gene-classes outputs/amr/gene_classes.tsv --out-png outputs/figures/amr_profile_dots.png --out-svg outputs/figures/amr_profile_dots.svg
```

La integracion usa `sample_id` como llave canonica para evitar mismatch entre arbol y resistoma.
