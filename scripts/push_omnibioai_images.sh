#!/usr/bin/env bash

set -euo pipefail

###############################################################################
# OmniBioAI Stable Push Pipeline (Sylabs + GHCR)
###############################################################################

SYLABS_USER="man4ishg"
SYLABS_COLLECTION="omnibioai"

GHCR_USER="man4ishg"
GHCR_REPO="omnibioai"

SIF_DIR="sif"
LOG_FILE="push_omnibioai.log"

> "$LOG_FILE"

###############################################################################
# PUSH FUNCTIONS
###############################################################################

push_sylabs() {
    local sif="$1"
    local tool
    tool=$(basename "$sif" _arm64.sif)

    local target="library://${SYLABS_USER}/${SYLABS_COLLECTION}/${tool}:arm64"

    echo "[SYLABS] $tool"

    singularity push -U "$sif" "$target" >> "$LOG_FILE" 2>&1
}

push_ghcr() {
    local sif="$1"
    local tool
    tool=$(basename "$sif" _arm64.sif)

    local image="ghcr.io/${GHCR_USER}/${GHCR_REPO}/${tool}:arm64"

    echo "[GHCR] $tool"

    # Simple OCI conversion
    tmp="/tmp/${tool}.tar"

    singularity build --docker-archive "$tmp" "$sif" >> "$LOG_FILE" 2>&1

    docker load -i "$tmp" >> "$LOG_FILE" 2>&1

    docker tag "${tool}:latest" "$image" >> "$LOG_FILE" 2>&1

    docker push "$image" >> "$LOG_FILE" 2>&1
}

###############################################################################
# MAIN LOOP (SAFE + RELIABLE)
###############################################################################

echo "Starting OmniBioAI Hybrid Pipeline..."

for sif in "$SIF_DIR"/*_arm64.sif; do
    tool=$(basename "$sif" _arm64.sif)

    echo "==================================================" | tee -a "$LOG_FILE"
    echo "Processing: $tool" | tee -a "$LOG_FILE"

    {
        push_sylabs "$sif"
        push_ghcr "$sif"
    } || {
        echo "[FAILED] $tool" | tee -a "$LOG_FILE"
        continue
    }

    echo "[DONE] $tool" | tee -a "$LOG_FILE"
done

echo "All uploads finished."