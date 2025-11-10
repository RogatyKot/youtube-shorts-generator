output "generated_shorts_bucket" {
  value = google_storage_bucket.generated_shorts.name
}
output "media_assets_bucket" {
  value = google_storage_bucket.media_assets.name
}
