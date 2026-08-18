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
variable "enable_managed_data_plane" {
  type    = bool
  default = false
}
variable "private_subnet_id" {
  type    = string
  default = ""
}
variable "private_dns_zone_id" {
  type    = string
  default = ""
}
variable "data_admin_login" {
  type    = string
  default = "taxflow_admin"
}
variable "data_admin_password" {
  type      = string
  sensitive = true
  default   = null
}
variable "redis_sku" {
  type    = string
  default = "Premium"
}
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

resource "azurerm_log_analytics_workspace" "observability" {
  name                = "law-${module.platform_contract.name}"
  location            = var.region
  resource_group_name = azurerm_resource_group.platform.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = module.platform_contract.tags
}

resource "azurerm_postgresql_flexible_server" "aurora_equivalent" {
  count                         = var.enable_managed_data_plane ? 1 : 0
  name                          = "${module.platform_contract.name}-postgres"
  resource_group_name           = azurerm_resource_group.platform.name
  location                      = var.region
  version                       = "16"
  administrator_login           = var.data_admin_login
  administrator_password        = var.data_admin_password
  delegated_subnet_id           = var.private_subnet_id
  private_dns_zone_id           = var.private_dns_zone_id
  public_network_access_enabled = false
  storage_mb                    = 131072
  sku_name                      = "GP_Standard_D4s_v3"
  backup_retention_days         = 35
  geo_redundant_backup_enabled  = var.environment == "prod"
  tags                          = module.platform_contract.tags
}

resource "azurerm_eventhub_namespace" "events" {
  count                         = var.enable_managed_data_plane ? 1 : 0
  name                          = "${module.platform_contract.name}-events"
  location                      = var.region
  resource_group_name           = azurerm_resource_group.platform.name
  sku                           = "Standard"
  capacity                      = 2
  auto_inflate_enabled          = true
  maximum_throughput_units      = 10
  public_network_access_enabled = false
  minimum_tls_version           = "1.2"
  tags                          = module.platform_contract.tags
}

resource "azurerm_redis_cache" "cache" {
  count                         = var.enable_managed_data_plane ? 1 : 0
  name                          = "${module.platform_contract.name}-redis"
  location                      = var.region
  resource_group_name           = azurerm_resource_group.platform.name
  capacity                      = 1
  family                        = "P"
  sku_name                      = var.redis_sku
  minimum_tls_version           = "1.2"
  public_network_access_enabled = false
  non_ssl_port_enabled          = false
  redis_version                 = "6"
  tags                          = module.platform_contract.tags
}
