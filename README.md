# OmniBioAI Tool Images

ARM64-compatible Docker/Singularity images for bioinformatics and ML tools
running on DGX Spark via Slurm.

> **100 SIF images · 64G total · ARM64 (aarch64)**

## Structure

```
omnibioai-tool-images/
├── dockerfiles/          ← one Dockerfile per tool
├── sif/                  ← built Singularity SIF images (gitignored)
├── build_logs/           ← build output logs (gitignored)
├── tests/                ← pytest test suite (97% coverage)
└── build_all.sh          ← build script
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
3. Add tool entry to `omnibioai-tes/configs/tools.example.yaml`
4. Restart TES — done!

---

## Tools Available (100 total)

### Bio Core (10)

| Tool | Image | Size |
|------|-------|------|
| fastqc | `sif/fastqc_arm64.sif` | 304M |
| multiqc | `sif/multiqc_arm64.sif` | 658M |
| trimmomatic | `sif/trimmomatic_arm64.sif` | 282M |
| samtools | `sif/samtools_arm64.sif` | 76M |
| bcftools | `sif/bcftools_arm64.sif` | 87M |
| bwa | `sif/bwa_arm64.sif` | 83M |
| star | `sif/star_arm64.sif` | 73M |
| featurecounts | `sif/featurecounts_arm64.sif` | 76M |
| gatk | `sif/gatk_arm64.sif` | 989M |
| deseq2 | `sif/deseq2_arm64.sif` | 461M |

### Variant Analysis (10)

| Tool | Image | Size |
|------|-------|------|
| vcftools | `sif/vcftools_arm64.sif` | 89M |
| snpeff | `sif/snpeff_arm64.sif` | 345M |
| vep | `sif/vep_arm64.sif` | 602M |
| plink | `sif/plink_arm64.sif` | 88M |
| freebayes | `sif/freebayes_arm64.sif` | 73M |
| strelka2 | `sif/strelka2_arm64.sif` | 235M |
| gatk *(mutect2)* | `sif/gatk_arm64.sif` | reused |
| bcftools *(filter)* | `sif/bcftools_arm64.sif` | reused |
| plink *(gwas)* | `sif/plink_arm64.sif` | reused |
| vcftools *(filter)* | `sif/vcftools_arm64.sif` | reused |

### RNA-seq (10)

| Tool | Image | Size |
|------|-------|------|
| kallisto | `sif/kallisto_arm64.sif` | 77M |
| salmon | `sif/salmon_arm64.sif` | 76M |
| hisat2 | `sif/hisat2_arm64.sif` | 102M |
| stringtie | `sif/stringtie_arm64.sif` | 88M |
| rsem | `sif/rsem_arm64.sif` | 386M |
| edger | `sif/edger_arm64.sif` | 390M |
| limma | `sif/limma_arm64.sif` | 390M |
| dexseq | `sif/dexseq_arm64.sif` | 526M |
| rmats | `sif/rmats_arm64.sif` | 349M |
| tximport | `sif/tximport_arm64.sif` | 377M |

### Metagenomics (10)

| Tool | Image | Size |
|------|-------|------|
| kraken2 | `sif/kraken2_arm64.sif` | 118M |
| bracken | `sif/bracken_arm64.sif` | 85M |
| metaphlan | `sif/metaphlan_arm64.sif` | 487M |
| humann3 | `sif/humann3_arm64.sif` | 807M |
| diamond | `sif/diamond_arm64.sif` | 75M |
| prodigal | `sif/prodigal_arm64.sif` | 73M |
| prokka | `sif/prokka_arm64.sif` | 633M |
| checkm | `sif/checkm_arm64.sif` | 406M |
| quast | `sif/quast_arm64.sif` | 283M |
| spades | `sif/spades_arm64.sif` | 85M |

### Epigenomics (10)

| Tool | Image | Size |
|------|-------|------|
| bismark | `sif/bismark_arm64.sif` | 101M |
| macs2 | `sif/macs2_arm64.sif` | 85M |
| deeptools | `sif/deeptools_arm64.sif` | 460M |
| homer | `sif/homer_arm64.sif` | 101M |
| atacqc | `sif/atacqc_arm64.sif` | 1.4G |
| chromhmm | `sif/chromhmm_arm64.sif` | 285M |
| epic2 | `sif/epic2_arm64.sif` | 85M |
| bedtools | `sif/bedtools_arm64.sif` | 73M |
| bismark *(extractor)* | `sif/bismark_arm64.sif` | reused |
| deeptools *(matrix)* | `sif/deeptools_arm64.sif` | reused |

### Single-cell (9)

| Tool | Image | Size |
|------|-------|------|
| seurat | `sif/seurat_arm64.sif` | 559M |
| harmony | `sif/harmony_arm64.sif` | 566M |
| monocle3 | `sif/monocle3_arm64.sif` | 462M |
| scrublet | `sif/scrublet_arm64.sif` | 632M |
| scenic | `sif/scenic_arm64.sif` | 750M |
| signac | `sif/signac_arm64.sif` | 616M |
| doubletfinder | `sif/doubletfinder_arm64.sif` | 563M |
| velocyto | `sif/velocyto_arm64.sif` | — |
| cellranger | ⚠️ needs 10x license | — |

### Proteomics (10)

| Tool | Image | Size |
|------|-------|------|
| msfragger | `sif/msfragger_arm64.sif` | ⚠️ needs license |
| flashlfq | `sif/flashlfq_arm64.sif` | 138M |
| percolator | `sif/percolator_arm64.sif` | — |
| philosopher | `sif/philosopher_arm64.sif` | 97M |
| maxquant | `sif/maxquant_arm64.sif` | 314M |
| moff | `sif/moff_arm64.sif` | — |
| ionquant | `sif/ionquant_arm64.sif` | 493M |
| skyline | `sif/skyline_arm64.sif` | 300M |
| fragpipe | `sif/fragpipe_arm64.sif` | — |
| tpp | `sif/tpp_arm64.sif` | 300M |

### Structural Biology (10)

| Tool | Image | Size |
|------|-------|------|
| autodock | `sif/autodock_arm64.sif` | 201M |
| pymol | `sif/pymol_arm64.sif` | 183M |
| rosetta | `sif/rosetta_arm64.sif` | 200M |
| gromacs | `sif/gromacs_arm64.sif` | 162M |
| openmm | `sif/openmm_arm64.sif` | 262M |
| modeller | `sif/modeller_arm64.sif` | 200M |
| hmmer | `sif/hmmer_arm64.sif` | 75M |
| pdbfixer | `sif/pdbfixer_arm64.sif` | 262M |
| muscle | `sif/muscle_arm64.sif` | 72M |
| iqtree | `sif/iqtree_arm64.sif` | 76M |

### ML / AI (10)

| Tool | Image | Size |
|------|-------|------|
| pytorch | `sif/pytorch_arm64.sif` | 5.7G |
| tensorflow | `sif/tensorflow_arm64.sif` | 884M |
| huggingface | `sif/huggingface_arm64.sif` | 5.8G |
| sklearn | `sif/sklearn_arm64.sif` | 407M |
| xgboost | `sif/xgboost_arm64.sif` | 1.4G |
| rapids | `sif/rapids_arm64.sif` | 498M |
| esm2 | `sif/esm2_arm64.sif` | 5.6G |
| alphafold2 | `sif/alphafold2_arm64.sif` | 6.5G |
| cellpose | `sif/cellpose_arm64.sif` | 5.9G |
| scanpy | `sif/scanpy_arm64.sif` | 621M |

### More Bioinformatics (11)

| Tool | Image | Size |
|------|-------|------|
| busco | `sif/busco_arm64.sif` | 85M |
| minimap2 | `sif/minimap2_arm64.sif` | 76M |
| medaka | `sif/medaka_arm64.sif` | 88M |
| nanostat | `sif/nanostat_arm64.sif` | 315M |
| flye | `sif/flye_arm64.sif` | 85M |
| repeatmasker | `sif/repeatmasker_arm64.sif` | 99M |
| trinity | `sif/trinity_arm64.sif` | 101M |
| transdecoder | `sif/transdecoder_arm64.sif` | 83M |
| interproscan | `sif/interproscan_arm64.sif` | 5.8G |
| orthofinder | `sif/orthofinder_arm64.sif` | 88M |
| augustus | `sif/augustus_arm64.sif` | 116M |

### Population Genetics / GWAS (12)

| Tool | Image | Size |
|------|-------|------|
| admixture | `sif/admixture_arm64.sif` | 74M |
| eigensoft | `sif/eigensoft_arm64.sif` | 262M |
| beagle | `sif/beagle_arm64.sif` | 282M |
| shapeit | `sif/shapeit_arm64.sif` | 335M |
| gcta | `sif/gcta_arm64.sif` | 440M |
| ldsc | `sif/ldsc_arm64.sif` | 405M |
| plink2 | `sif/plink2_arm64.sif` | 393M |
| regenie | `sif/regenie_arm64.sif` | 355M |
| saige | `sif/saige_arm64.sif` | 430M |
| metal | `sif/metal_arm64.sif` | 212M |
| structure | `sif/structure_arm64.sif` | 333M |
| impute2 | `sif/impute2_arm64.sif` | 74M |

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
- SIF files are stored in `sif/` (gitignored — 64G total)
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