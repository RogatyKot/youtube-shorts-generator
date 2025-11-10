#!/usr/bin/env bash
set -e
echo "Local docker build (optional). Replace with gcloud builds or CI for real deployment."
docker build -t trend-analyzer:local -f docker/trend-analyzer/Dockerfile docker/trend-analyzer
docker build -t shorts-orchestrator:local -f docker/shorts-orchestrator/Dockerfile docker/shorts-orchestrator
docker build -t youtube-publisher:local -f docker/youtube-publisher/Dockerfile docker/youtube-publisher
echo "Images built: trend-analyzer, shorts-orchestrator, youtube-publisher"
