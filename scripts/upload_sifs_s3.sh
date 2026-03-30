#!/bin/bash
set -euo pipefail

BUCKET="${S3_SIF_BUCKET:-omnibioai-sif}"
REGION="${AWS_REGION:-us-east-1}"
SIF_DIR="$(dirname $0)/../sif"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Create bucket if not exists
aws s3 mb "s3://${BUCKET}-${ACCOUNT_ID}" --region "$REGION" 2>/dev/null || true
BUCKET="${BUCKET}-${ACCOUNT_ID}"

echo "Uploading SIFs to s3://${BUCKET}/"
for sif in "$SIF_DIR"/*.sif; do
    name=$(basename "$sif")
    size=$(du -sh "$sif" | cut -f1)
    echo "  [$size] $name ..."
    aws s3 cp "$sif" "s3://${BUCKET}/${name}" \
        --storage-class STANDARD_IA \
        --no-progress \
        --region "$REGION"
done

echo ""
echo "Done! SIF URIs:"
aws s3 ls "s3://${BUCKET}/" | awk '{print "  s3://'${BUCKET}'/" $4}'
