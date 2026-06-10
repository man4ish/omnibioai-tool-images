# OmniBioAI Tool Images

ARM64-compatible Docker/Singularity images for bioinformatics and ML tools
running on DGX Spark via Slurm.

> **459 SIF images · ~235G total · ARM64 (aarch64)**

## Structure

```
omnibioai-tool-images/
├── dockerfiles/          ← 454 Dockerfiles, one per tool
├── sif/                  ← built Singularity SIF images (gitignored)
├── build_logs/           ← build output logs (gitignored)
├── tests/                ← pytest test suite (97% coverage)
├── build_all.sh          ← build all images
└── build_missing_sifs.sh ← rebuild only missing/failed SIFs
```

## Quick Start

```bash
# Build a single tool
bash build_all.sh fastqc

# Build all tools
bash build_all.sh

# Build in parallel (N workers)
bash build_all.sh --parallel 4

# Run tests
pytest tests/ -v -k "not test_tool_runs_in_sif"
```

## Add a New Tool

1. Write `dockerfiles/Dockerfile.toolname`
2. Run `bash build_all.sh toolname`
3. Add tool entry to `omnibioai-tes/configs/tools/<domain>.yaml` (edit the appropriate category file)
4. Run `make restart` in `omnibioai-tes` — done!

---

## Tools Available (459 SIF images · 29 domains)

Tool configurations live in `omnibioai-tes/configs/tools/` — one YAML file per domain.

| # | Domain | Config file | Tools | Examples |
|---|--------|-------------|-------|---------|
| 01 | QC & Preprocessing | `01_qc_preprocessing.yaml` | 35 | FastQC, MultiQC, Trimmomatic |
| 02 | Alignment | `02_alignment.yaml` | 31 | BWA-MEM, BLASTN, Samtools |
| 03 | RNA-seq | `03_rnaseq.yaml` | 58 | DESeq2, Kallisto, featureCounts |
| 04 | Variant Analysis | `04_variants.yaml` | 57 | GATK, BCFtools, VEP |
| 05 | Epigenomics | `05_epigenomics.yaml` | 36 | Bismark, MACS2, deepTools |
| 06 | Single-cell | `06_single_cell.yaml` | 45 | Seurat, Scanpy, Cell Ranger |
| 07 | Spatial Omics | `07_spatial.yaml` | 11 | Cellpose, Space Ranger, Squidpy |
| 08 | Assembly | `08_assembly.yaml` | 20 | SPAdes, Flye, QUAST |
| 09 | Metagenomics | `09_metagenomics.yaml` | 30 | Kraken2, MetaPhlAn, HUMAnN3 |
| 10 | Microbiome | `10_microbiome.yaml` | 18 | QIIME2, nf-core Ampliseq |
| 11 | Population Genetics | `11_population_genetics.yaml` | 29 | ADMIXTURE, GCTA, REGENIE |
| 12 | Structural Biology | `12_structural_biology.yaml` | 27 | AlphaFold2, AutoDock, ESM-2 |
| 13 | Immunogenomics | `13_immunogenomics.yaml` | 6 | MiXCR, TRUST4, arcasHLA |
| 14 | Ancient DNA | `14_ancient_dna.yaml` | 1 | EAGER2 |
| 15 | Metabolomics | `15_metabolomics.yaml` | 5 | XCMS, MZmine3, SIRIUS |
| 16 | Drug Discovery | `16_drug_discovery.yaml` | 1 | ADMET Prediction |
| 17 | Proteomics | `17_proteomics.yaml` | 14 | MSFragger, Percolator, Philosopher |
| 18 | ML / DL | `18_ml_dl.yaml` | 19 | PyTorch, TensorFlow, RAPIDS |
| 19 | Cancer Genomics | `19_cancer_genomics.yaml` | 10 | AMBER, COBALT, Survival KM |
| 20 | Comparative Genomics | `20_comparative_genomics.yaml` | 8 | OrthoFinder, MCScan |
| 21 | Multi-omics | `21_multiomics.yaml` | 4 | MOFA+, MOSCOT |
| 22 | Proteogenomics | `22_proteogenomics.yaml` | 4 | TransDecoder, PRICE, Xtail |
| 23 | nf-core Pipelines | `23_nfcore_pipelines.yaml` | 2 | nf-core RNA-seq, Nanoseq |
| 24 | Annotation | `24_annotation.yaml` | 4 | RepeatMasker, AUGUSTUS, DAVID |
| 25 | Genomic Utilities | `25_genomic_utilities.yaml` | 3 | BEDTools, BEDOPS, PyMOL |
| 26 | Long Read | `26_longread.yaml` | 6 | Guppy, Dorado, Medaka |
| 27 | CRISPR | `27_crispr.yaml` | 9 | MAGeCK, Cas-OFFinder |
| 28 | Imaging | `28_imaging.yaml` | 2 | Steinbock, MCMICRO |
| 29 | HTTP Tools | `29_http_tools.yaml` | 512 | Enrichr, OmniBioAI Workflow Runner |

---

## Testing

```bash
# Run all tests (excluding live SIF execution)
pytest tests/ -v -k "not test_tool_runs_in_sif"

# Run with coverage
pytest tests/ --cov=tests --cov-report=term-missing \
  -k "not test_tool_runs_in_sif"

# Run including SIF execution tests (requires Singularity)
pytest tests/ -v
```

**Test results: 1026 passed · 97% coverage · 2.45s**

---

## Notes

- All images are built for `linux/arm64` (aarch64) — DGX Spark / Grace Hopper
- SIF files are stored in `sif/` (gitignored — ~235G total)
- Tools marked ⚠️ require an external license or manual download
- Tools reusing an existing SIF are noted as `reused`
- Build logs are in `build_logs/` (gitignored)

## Related Repos

| Repo | Description |
|------|-------------|
| `omnibioai-tes` | Tool Execution Service — orchestrates Slurm jobs |
| `omnibioai-tool-runtime` | Containerized tool runner |
| `omnibioai` | Main Django application |
| `omnibioai-toolserver` | HTTP ToolServer shim |