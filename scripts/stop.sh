#!/usr/bin/env bash
set -e
container_name="pm-mvp-container"

docker stop "$container_name" 2>/dev/null || true
docker rm "$container_name" 2>/dev/null || true

echo "Stopped pm-mvp-container"
