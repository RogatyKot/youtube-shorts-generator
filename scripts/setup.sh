#!/usr/bin/env bash
set -e
echo "Setup script: create venv and install local dependencies (for dev)"
python3 -m venv venv
source venv/bin/activate
pip install -r docker/trend-analyzer/requirements.txt
pip install -r docker/shorts-orchestrator/requirements.txt
pip install -r docker/youtube-publisher/requirements.txt
echo "Done. To run services, see README.md"
