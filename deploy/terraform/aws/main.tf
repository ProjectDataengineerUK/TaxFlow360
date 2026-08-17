terraform {
  required_version = ">= 1.7.0"
  required_providers { aws = { source = "hashicorp/aws", version = "~> 5.0" } }
}

variable "environment" { type = string }
variable "region" { type = string }
variable "data_residency" {
  type    = string
  default = "BR"
}
variable "databricks_workspace_url" { type = string }
provider "aws" {
  region = var.region
}

module "platform_contract" {
  source                   = "../modules/platform"
  environment              = var.environment
  region                   = var.region
  data_residency           = var.data_residency
  databricks_workspace_url = var.databricks_workspace_url
  tags                     = { cloud = "aws" }
}

resource "aws_kms_key" "lakehouse" {
  description             = "TaxFlow lakehouse encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  tags                    = module.platform_contract.tags
}

resource "aws_s3_bucket" "lakehouse" {
  bucket_prefix = "${module.platform_contract.name}-lakehouse-"
  tags          = module.platform_contract.tags
}
resource "aws_s3_bucket_public_access_block" "lakehouse" {
  bucket                  = aws_s3_bucket.lakehouse.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
resource "aws_s3_bucket_server_side_encryption_configuration" "lakehouse" {
  bucket = aws_s3_bucket.lakehouse.id
  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.lakehouse.arn
      sse_algorithm     = "aws:kms"
    }
  }
}
resource "aws_s3_bucket_versioning" "lakehouse" {
  bucket = aws_s3_bucket.lakehouse.id
  versioning_configuration { status = "Enabled" }
}

output "storage_uri" { value = "s3://${aws_s3_bucket.lakehouse.id}" }
output "databricks_workspace_url" { value = module.platform_contract.databricks_workspace_url }
output "regulatory_ai_search_endpoint" { value = module.platform_contract.ai_search_endpoint_name }
output "regulatory_model_gateway" { value = module.platform_contract.model_gateway_endpoint }
