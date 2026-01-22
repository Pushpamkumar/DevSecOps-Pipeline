#!/bin/bash
# Build insecure image that will fail security scanning
# This demonstrates the CI/CD security gates

set -e

echo "================================"
echo "Building INSECURE Docker Image"
echo "================================"

cd "$(dirname "$0")"/..

IMAGE_NAME="ml-service:insecure"
IMAGE_TAG="ml-service:insecure-latest"

docker build \
    -f docker/Dockerfile.insecure \
    -t "$IMAGE_NAME" \
    -t "$IMAGE_TAG" \
    --label "build.insecure=true" \
    --label "build.timestamp=$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
    .

echo "Image built: $IMAGE_NAME"
echo "To scan this image, run: trivy image $IMAGE_NAME"
