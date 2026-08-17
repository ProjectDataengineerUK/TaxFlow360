variable "project_name" {
  description = "Stable lowercase workload name."
  type        = string
  default     = "taxflow360"
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,30}$", var.project_name))
    error_message = "project_name must be a lowercase DNS-compatible name."
  }
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be dev, staging, or prod."
  }
}

variable "region" {
  type = string
}
variable "data_residency" {
  type = string
}
variable "databricks_workspace_url" {
  description = "Existing Databricks workspace URL; authentication uses workload identity."
  type        = string
  nullable    = false
  validation {
    condition     = startswith(var.databricks_workspace_url, "https://")
    error_message = "databricks_workspace_url must use HTTPS."
  }
}
variable "tags" {
  type    = map(string)
  default = {}
}

locals {
  name = "${var.project_name}-${var.environment}"
  mandatory_tags = merge(var.tags, {
    application     = var.project_name
    environment     = var.environment
    data_residency  = var.data_residency
    managed_by      = "terraform"
  })
}

output "name" {
  value = local.name
}
output "tags" {
  value = local.mandatory_tags
}
output "databricks_workspace_url" {
  value = var.databricks_workspace_url
}
variable "regulatory_snapshot_retention_days" {
  description = "Minimum retention for immutable official-source snapshots."
  type        = number
  default     = 2555
  validation {
    condition     = var.regulatory_snapshot_retention_days >= 365
    error_message = "regulatory snapshots require at least one year retention."
  }
}
variable "ai_search_endpoint_name" {
  description = "Existing governed Databricks AI Search endpoint; never a credential."
  type        = string
  default     = "taxflow-regulatory-search"
}
variable "model_gateway_endpoint" {
  description = "HTTPS gateway with no-training and retention controls."
  type        = string
  default     = "https://models.example.invalid"
  validation {
    condition     = startswith(var.model_gateway_endpoint, "https://")
    error_message = "model gateway must use HTTPS."
  }
}
output "ai_search_endpoint_name" { value = var.ai_search_endpoint_name }
output "model_gateway_endpoint" { value = var.model_gateway_endpoint }
