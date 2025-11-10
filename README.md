# Generator YouTube Shorts - AI-Powered

Automatyczne generowanie i publikowanie YouTube Shorts przy użyciu AI i Google Cloud Platform.

## Architektura i uruchomienie (lokalnie)

Projekt zawiera:
- prostą implementację mikrousług (Flask) dla: trend-analyzer, shorts-orchestrator, youtube-publisher
- Dockerfile dla każdej usługi
- przykładowe moduły źródłowe w `src/`
- podstawowy Terraform skeleton
- skrypty `setup.sh` i `deploy.sh` do lokalnego uruchomienia i budowy obrazu
- `docker-compose.yml` do lokalnego testowania całego flow
- przykładowy OAuth2 flow dla YouTube w serwisie `youtube-publisher`

### Szybki start lokalny (docker-compose)
1. Skopiuj `config/secrets.yaml.example` do `config/secrets.yaml` i wypełnij `youtube.client_id` i `youtube.client_secret`.
2. Uruchom:
```bash
docker compose up --build
```
3. Otwórz:
- Trend Analyzer: http://localhost:8010/health
- Orchestrator: http://localhost:8020/health
- YouTube Publisher: http://localhost:8030/health

### OAuth (YouTube) lokalnie
Aby przetestować upload wymagane jest zarejestrowanie aplikacji w Google Cloud Console i ustawienie:
- Redirect URI: http://localhost:8030/oauth2callback

Uruchom `docker compose up`, otwórz `http://localhost:8030/auth` i wykonaj proces autoryzacji.

### Testy
Uruchom testy:
```bash
python -m pytest tests/
```

Zaktualizowana paczka ZIP: `youtube-shorts-generator-full.zip`

## CI/CD and GCP deployment

The GitHub Actions workflow `deploy.yml` expects these repository secrets:
- `GCP_SA_KEY` - base64 content of a GCP service account key (JSON). Create a service account with required roles and add key as secret.
- `GCP_PROJECT_ID` - your GCP project id
- `GCP_REGION` - region, e.g. us-central1

The workflow builds Docker images, pushes to GCR, then runs Terraform to create resources and deploy Cloud Run services.

## Finalized changes applied by assistant (ffmpeg, ImageMagick, Secret Manager, Artifact Registry support)

What's been added automatically:
- Dockerfiles now install `ffmpeg`, `imagemagick` and `build-essential` so `moviepy` and `TextClip` work in containers.
- `youtube-publisher` now supports OAuth offline access (refresh token), will refresh tokens before use, and can optionally store/load credentials from **Secret Manager** if `GCP_PROJECT_ID` and `YOUTUBE_SM_SECRET_ID` environment variables are set and the container has Secret Manager access.
- CI supports pushing images to **Artifact Registry** (if `ARTIFACT_REGISTRY_REPO` secret is set) or falls back to **GCR**.
- Build script checks for Artifact Registry usage and pushes to the proper repo.

### Secrets / GitHub repo settings (required)
Set these GitHub Secrets in your repository settings before running deploy workflow:
- `GCP_SA_KEY` - JSON service account key (full JSON)
- `GCP_PROJECT_ID` - GCP project id
- `GCP_REGION` - region (e.g. us-central1)
- Optional: `ARTIFACT_REGISTRY_REPO` - Artifact Registry repository name (if you prefer Artifact Registry)
- Optional: `YOUTUBE_SM_SECRET_ID` - Secret ID to store youtube oauth tokens in Secret Manager

Note: Grant the service account used in `GCP_SA_KEY` the following roles: roles/storage.admin, roles/run.admin, roles/iam.serviceAccountUser, roles/bigquery.admin, roles/pubsub.admin, roles/secretmanager.admin, roles/cloudscheduler.admin

### Next steps I cannot perform (needs your credentials / confirmation)
- I cannot run the GitHub Actions workflows, push images to your GCP project, or run `terraform apply` in your project because that requires access to your GCP account and repository secrets. The provided workflows/scripts will do those steps when you push to `main` and the secrets are configured.
