#!/bin/bash

# Taken from kaeru (https://github.com/R0rt1z2/kaeru),
# AGPL-3.0 (c) Roger Ortiz

CONTAINER_NAME="penumbra"
DOCKERFILE="Dockerfile"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

FORCE_REBUILD=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--force)
            FORCE_REBUILD=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [-f|--force]"
            echo "  -f, --force    Force rebuild of the Docker image"
            exit 1
            ;;
    esac
done

if [ "$FORCE_REBUILD" = true ] || ! docker image inspect "$CONTAINER_NAME" &> /dev/null; then
    if [ "$FORCE_REBUILD" = true ]; then
        echo "Force rebuilding container..."
    else
        echo "Container not found, building..."
    fi
    docker build -t "$CONTAINER_NAME" -f "$SCRIPT_DIR/$DOCKERFILE" "$SCRIPT_DIR"
fi

docker run -it --rm \
    -v "$SCRIPT_DIR:/penumbra" \
    -w /penumbra \
    "$CONTAINER_NAME" \
    bash
