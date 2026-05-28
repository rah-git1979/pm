#!/usr/bin/env bash
set -e
container_name="pm-mvp-container"

docker build -t pm-mvp .

docker stop "$container_name" 2>/dev/null || true
docker rm "$container_name" 2>/dev/null || true

docker run -d --name "$container_name" -p 8000:8000 pm-mvp

echo "Started pm-mvp-container on http://localhost:8000"
