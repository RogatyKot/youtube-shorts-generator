resource "google_storage_bucket" "media_assets" {
  name     = "${var.project_id}-media-assets"
  location = var.region
  uniform_bucket_level_access = true
  force_destroy = true
}

resource "google_storage_bucket" "generated_shorts" {
  name     = "${var.project_id}-generated-shorts"
  location = var.region
  uniform_bucket_level_access = true
  force_destroy = true
}
