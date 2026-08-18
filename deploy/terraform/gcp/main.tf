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
variable "enable_managed_data_plane" {
  type    = bool
  default = false
}
variable "private_network" {
  type    = string
  default = ""
}
variable "database_tier" {
  type    = string
  default = "db-custom-4-16384"
}
variable "redis_memory_gb" {
  type    = number
  default = 4
}
provider "google" {
  project = var.project_id
  region  = var.region
}

module "platform_contract" {
  source                   = "../modules/platform"
  environment              = var.environment
  region                   = var.region
  data_residency           = var.data_residency
  databricks_workspace_url = var.databricks_workspace_url
  tags                     = { cloud = "gcp" }
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
  name                        = "${var.project_id}-${module.platform_contract.name}-lakehouse"
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

resource "google_logging_project_sink" "audit" {
  name                   = "${module.platform_contract.name}-audit"
  destination            = "logging.googleapis.com/projects/${var.project_id}"
  filter                 = "labels.application=\"${var.project_id}\""
  unique_writer_identity = true
}

resource "google_sql_database_instance" "postgres" {
  count               = var.enable_managed_data_plane ? 1 : 0
  name                = "${module.platform_contract.name}-postgres"
  database_version    = "POSTGRES_16"
  region              = var.region
  deletion_protection = var.environment == "prod"
  settings {
    tier              = var.database_tier
    availability_type = "REGIONAL"
    disk_type         = "PD_SSD"
    disk_size         = 100
    disk_autoresize   = true
    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
    }
    ip_configuration {
      ipv4_enabled                                  = false
      private_network                               = var.private_network
      enable_private_path_for_google_cloud_services = true
    }
  }
}

resource "google_pubsub_topic" "events" {
  count  = var.enable_managed_data_plane ? 1 : 0
  name   = "${module.platform_contract.name}-events"
  labels = module.platform_contract.tags
}

resource "google_pubsub_topic" "events_dlq" {
  count  = var.enable_managed_data_plane ? 1 : 0
  name   = "${module.platform_contract.name}-events-dlq"
  labels = module.platform_contract.tags
}

resource "google_redis_instance" "cache" {
  count                   = var.enable_managed_data_plane ? 1 : 0
  name                    = "${module.platform_contract.name}-redis"
  tier                    = "STANDARD_HA"
  memory_size_gb          = var.redis_memory_gb
  region                  = var.region
  redis_version           = "REDIS_7_2"
  authorized_network      = var.private_network
  transit_encryption_mode = "SERVER_AUTHENTICATION"
  auth_enabled            = true
  labels                  = module.platform_contract.tags
}
