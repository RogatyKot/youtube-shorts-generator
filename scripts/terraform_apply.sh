#!/usr/bin/env bash
set -euo pipefail
PROJECT_ID="${1:-${PROJECT_ID}}"
REGION="${2:-us-central1}"
cd terraform
terraform init -input=false
terraform apply -auto-approve -var="project_id=${PROJECT_ID}" -var="region=${REGION}"
