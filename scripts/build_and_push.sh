#!/usr/bin/env bash
set -euo pipefail
PROJECT_ID="${1:-${PROJECT_ID}}"
ARTIFACT_REGISTRY_REPO="${2:-${ARTIFACT_REGISTRY_REPO:-}}"
REGION="${3:-us-central1}"

if [ -n "$ARTIFACT_REGISTRY_REPO" ]; then
  # Example: LOCATION-docker.pkg.dev/$PROJECT_ID/$REPO/image:tag
  echo "Using Artifact Registry repo: $ARTIFACT_REGISTRY_REPO"
  docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/trend-analyzer:latest -f docker/trend-analyzer/Dockerfile docker/trend-analyzer
  docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/shorts-orchestrator:latest -f docker/shorts-orchestrator/Dockerfile docker/shorts-orchestrator
  docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/youtube-publisher:latest -f docker/youtube-publisher/Dockerfile docker/youtube-publisher
  docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/trend-analyzer:latest
  docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/shorts-orchestrator:latest
  docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/youtube-publisher:latest
else
  echo "Using GCR (gcr.io)"
  docker build -t gcr.io/${PROJECT_ID}/trend-analyzer:latest -f docker/trend-analyzer/Dockerfile docker/trend-analyzer
  docker build -t gcr.io/${PROJECT_ID}/shorts-orchestrator:latest -f docker/shorts-orchestrator/Dockerfile docker/shorts-orchestrator
  docker build -t gcr.io/${PROJECT_ID}/youtube-publisher:latest -f docker/youtube-publisher/Dockerfile docker/youtube-publisher
  docker push gcr.io/${PROJECT_ID}/trend-analyzer:latest
  docker push gcr.io/${PROJECT_ID}/shorts-orchestrator:latest
  docker push gcr.io/${PROJECT_ID}/youtube-publisher:latest
fi
echo "Images pushed"
