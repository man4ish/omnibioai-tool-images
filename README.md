# OmniBioAI Tool Images

ARM64-compatible Docker/Singularity images for bioinformatics and ML tools
running on DGX Spark via Slurm.

## Structure
```
omnibioai-tool-images/
├── dockerfiles/          ← one Dockerfile per tool
├── sif/                  ← built Singularity SIF images
├── build_logs/           ← build output logs
└── build_all.sh          ← build script
```

## Add a new tool
1. Write `dockerfiles/Dockerfile.toolname`
2. Run `bash build_all.sh toolname`
3. Add tool to `omnibioai-tes/configs/tools.example.yaml`
4. Restart TES — done!

## Build all tools
```bash
bash build_all.sh
```

## Build single tool
```bash
bash build_all.sh fastqc
```

## Tools available
| Tool | Image | Status |
|------|-------|--------|
| fastqc | sif/fastqc_arm64.sif | ✅ |
| multiqc | sif/multiqc_arm64.sif | 🔨 |
| trimmomatic | sif/trimmomatic_arm64.sif | 🔨 |
| samtools | sif/samtools_arm64.sif | 🔨 |
| bwa | sif/bwa_arm64.sif | 🔨 |
| star | sif/star_arm64.sif | 🔨 |
| featurecounts | sif/featurecounts_arm64.sif | 🔨 |
| gatk | sif/gatk_arm64.sif | 🔨 |
| bcftools | sif/bcftools_arm64.sif | 🔨 |
| deseq2 | sif/deseq2_arm64.sif | 🔨 |
