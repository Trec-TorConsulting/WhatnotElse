#!/usr/bin/env bash
set -euo pipefail

IMAGE_TAG="${1:-latest}"
REGISTRY="registry.maddscientist.com/whatnot-else/erpnext-whatnot"

echo "==> Building WhatnotElse image: ${REGISTRY}:${IMAGE_TAG}..."

# Build multi-platform or native architecture
docker build \
    -t "${REGISTRY}:${IMAGE_TAG}" \
    -f Dockerfile .

echo "==> Pushing image to local registry: ${REGISTRY}:${IMAGE_TAG}..."
docker push "${REGISTRY}:${IMAGE_TAG}"

echo "==> Successfully built and pushed ${REGISTRY}:${IMAGE_TAG}"
