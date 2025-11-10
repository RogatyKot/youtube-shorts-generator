# Service accounts
resource "google_service_account" "trend_analyzer_sa" {
  account_id   = "trend-analyzer-sa"
  display_name = "Trend Analyzer Service Account"
}
resource "google_service_account" "orchestrator_sa" {
  account_id   = "orchestrator-sa"
  display_name = "Orchestrator Service Account"
}
resource "google_service_account" "publisher_sa" {
  account_id   = "youtube-publisher-sa"
  display_name = "YouTube Publisher Service Account"
}

# Cloud Run services (reference images to be pushed to gcr.io/${var.project_id}/... by CI)
resource "google_cloud_run_service" "trend_analyzer" {
  name     = "trend-analyzer"
  location = var.region
  template {
    spec {
      service_account_name = google_service_account.trend_analyzer_sa.email
      containers {
        image = "gcr.io/${var.project_id}/trend-analyzer:latest"
        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }
      }
    }
  }
  traffic { percent = 100 latest_revision = true }
}

resource "google_cloud_run_service" "shorts_orchestrator" {
  name     = "shorts-orchestrator"
  location = var.region
  template {
    spec {
      service_account_name = google_service_account.orchestrator_sa.email
      containers {
        image = "gcr.io/${var.project_id}/shorts-orchestrator:latest"
        env { name = "OUTPUT_BUCKET" value = google_storage_bucket.generated_shorts.name }
      }
    }
  }
  traffic { percent = 100 latest_revision = true }
}

resource "google_cloud_run_service" "youtube_publisher" {
  name     = "youtube-publisher"
  location = var.region
  template {
    spec {
      service_account_name = google_service_account.publisher_sa.email
      containers {
        image = "gcr.io/${var.project_id}/youtube-publisher:latest"
      }
    }
  }
  traffic { percent = 100 latest_revision = true }
}
