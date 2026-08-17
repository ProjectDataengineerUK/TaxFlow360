terraform {
  required_version = ">= 1.7.0"
  required_providers { azurerm = { source = "hashicorp/azurerm", version = "~> 4.0" } }
}

variable "environment" { type = string }
variable "region" { type = string }
variable "data_residency" {
  type    = string
  default = "BR"
}
variable "databricks_workspace_url" { type = string }
provider "azurerm" {
  features {}
}

module "platform_contract" {
  source                   = "../modules/platform"
  environment              = var.environment
  region                   = var.region
  data_residency           = var.data_residency
  databricks_workspace_url = var.databricks_workspace_url
  tags                     = { cloud = "azure" }
}

resource "azurerm_resource_group" "platform" {
  name     = "rg-${module.platform_contract.name}"
  location = var.region
  tags     = module.platform_contract.tags
}
resource "azurerm_storage_account" "lakehouse" {
  name                              = substr(replace("${module.platform_contract.name}lake", "-", ""), 0, 24)
  resource_group_name               = azurerm_resource_group.platform.name
  location                          = azurerm_resource_group.platform.location
  account_tier                      = "Standard"
  account_replication_type          = var.environment == "prod" ? "GRS" : "LRS"
  account_kind                      = "StorageV2"
  is_hns_enabled                    = true
  min_tls_version                   = "TLS1_2"
  public_network_access_enabled     = false
  shared_access_key_enabled         = false
  infrastructure_encryption_enabled = true
  blob_properties {
    versioning_enabled = true
  }
  tags = module.platform_contract.tags
}
resource "azurerm_storage_data_lake_gen2_filesystem" "lakehouse" {
  name               = "lakehouse"
  storage_account_id = azurerm_storage_account.lakehouse.id
}

output "storage_uri" { value = "abfss://${azurerm_storage_data_lake_gen2_filesystem.lakehouse.name}@${azurerm_storage_account.lakehouse.name}.dfs.core.windows.net" }
output "databricks_workspace_url" { value = module.platform_contract.databricks_workspace_url }
output "regulatory_ai_search_endpoint" { value = module.platform_contract.ai_search_endpoint_name }
output "regulatory_model_gateway" { value = module.platform_contract.model_gateway_endpoint }
