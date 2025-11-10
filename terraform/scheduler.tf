resource "google_cloud_scheduler_job" "trend_analysis" {
  name = "trend-analysis-scheduler"
  description = "Trigger trend analysis every 6 hours"
  schedule = "0 */6 * * *"
  time_zone = "UTC"

  http_target {
    http_method = "POST"
    uri = "https://${google_cloud_run_service.trend_analyzer.status[0].url}/analyze"
    oidc_token {
      service_account_email = google_service_account.trend_analyzer_sa.email
    }
  }
}
