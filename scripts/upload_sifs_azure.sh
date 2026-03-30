#!/bin/bash
set -euo pipefail

CONTAINER="${AZURE_SIF_CONTAINER:-omnibioai-sif}"
SIF_DIR="$(dirname $0)/../sif"

# Create container if not exists
az storage container create \
    --name "$CONTAINER" \
    --connection-string "$AZURE_STORAGE_CONNECTION_STRING" \
    2>/dev/null || true

echo "Uploading SIFs to azureblob container: ${CONTAINER}"
for sif in "$SIF_DIR"/*.sif; do
    name=$(basename "$sif")
    size=$(du -sh "$sif" | cut -f1)
    echo "  [$size] $name ..."
    az storage blob upload \
        --connection-string "$AZURE_STORAGE_CONNECTION_STRING" \
        --container-name "$CONTAINER" \
        --name "$name" \
        --file "$sif" \
        --tier Cool \
        --overwrite \
        --output none
done

echo "Done!"
