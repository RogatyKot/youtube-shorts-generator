variable "project_id" { description = "GCP Project ID" type = string }
variable "region" { description = "GCP Region" type = string default = "us-central1" }
variable "environment" { description = "Environment (dev/staging/prod)" type = string default = "dev" }
variable "service_account_key" { description = "Base64 encoded service account key" type = string default = "" }
