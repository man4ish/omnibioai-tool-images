#!/bin/bash
# Upload all ARM64 SIF images to Hugging Face
# Repo: https://huggingface.co/datasets/man4sihg/omnibioai-sif-images

REPO="man4sihg/omnibioai-sif-images"
SIF_DIR="sif"
LOG="build_logs/hf_push_$(date +%Y%m%d_%H%M%S).log"
PUSHED=0; SKIPPED=0; FAILED=0

mkdir -p build_logs
echo "=== HF Push $(date) ===" | tee "$LOG"

for sif in "$SIF_DIR"/*_arm64.sif; do
    filename=$(basename "$sif")
    echo -n "Uploading $filename ... " | tee -a "$LOG"
    if huggingface-cli upload "$REPO" "$sif" --repo-type dataset >> "$LOG" 2>&1; then
        echo "OK" | tee -a "$LOG"
        ((PUSHED++))
    else
        echo "FAILED" | tee -a "$LOG"
        ((FAILED++))
    fi
done

echo "" | tee -a "$LOG"
echo "=== Done: Pushed=$PUSHED Failed=$FAILED ===" | tee -a "$LOG"
