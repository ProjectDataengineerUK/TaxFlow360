terraform {
  required_version = ">= 1.7.0"
  required_providers { google = { source = "hashicorp/google", version = "~> 6.0" } }
}

variable "environment" { type = string }
variable "region" { type = string }
variable "project_id" { type = string }
variable "data_residency" {
  type    = string
  default = "BR"
}
variable "databricks_workspace_url" { type = string }
provider "google" { project = var.project_id; region = var.region }

module "platform_contract" {
  source = "../modules/platform"
  environment              = var.environment
  region                   = var.region
  data_residency           = var.data_residency
  databricks_workspace_url = var.databricks_workspace_url
  tags = { cloud = "gcp" }
}

resource "google_kms_key_ring" "lakehouse" {
  name     = "${module.platform_contract.name}-lake"
  location = var.region
}
resource "google_kms_crypto_key" "lakehouse" {
  name            = "lakehouse"
  key_ring        = google_kms_key_ring.lakehouse.id
  rotation_period = "7776000s"
}
resource "google_storage_bucket" "lakehouse" {
  name = "${var.project_id}-${module.platform_contract.name}-lakehouse"
  location                    = var.region
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  force_destroy               = false
  labels                      = module.platform_contract.tags
  encryption { default_kms_key_name = google_kms_crypto_key.lakehouse.id }
  versioning { enabled = true }
}

output "storage_uri" { value = "gs://${google_storage_bucket.lakehouse.name}" }
output "databricks_workspace_url" { value = module.platform_contract.databricks_workspace_url }
output "regulatory_ai_search_endpoint" { value = module.platform_contract.ai_search_endpoint_name }
output "regulatory_model_gateway" { value = module.platform_contract.model_gateway_endpoint }
