resource "google_pubsub_topic" "trend_data" {
  name = "youtube-shorts-trend-data"
}

resource "google_pubsub_subscription" "trend_analyzer_sub" {
  name  = "trend-analyzer-subscription"
  topic = google_pubsub_topic.trend_data.name
  ack_deadline_seconds = 600
}
