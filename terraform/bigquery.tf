resource "google_bigquery_dataset" "trends" {
  dataset_id = "youtube_trends_data"
  location   = "US"
  description = "YouTube Shorts trends data"
  default_table_expiration_ms = 7776000000
}

resource "google_bigquery_table" "trends_raw" {
  dataset_id = google_bigquery_dataset.trends.dataset_id
  table_id   = "trends_raw"
  schema     = <<EOF
[
  {"name": "videoId", "type": "STRING"},
  {"name": "title", "type": "STRING"},
  {"name": "views", "type": "INTEGER"},
  {"name": "publishedAt", "type": "TIMESTAMP"}
]
EOF
}
