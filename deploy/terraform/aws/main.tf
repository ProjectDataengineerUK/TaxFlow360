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
variable "enable_managed_data_plane" {
  description = "Enable Aurora, MSK and Redis only in an approved sandbox/prod plan."
  type        = bool
  default     = false
}
variable "private_subnet_ids" {
  description = "Private subnet IDs for managed data services; never public subnets."
  type        = list(string)
  default     = []
}
variable "data_security_group_id" {
  description = "Security group allowing only application workload identities."
  type        = string
  default     = ""
}
variable "aurora_instance_class" {
  type    = string
  default = "db.r7g.large"
}
variable "redis_node_type" {
  type    = string
  default = "cache.r7g.large"
}
variable "msk_broker_count" {
  type    = number
  default = 3
  validation {
    condition     = var.msk_broker_count >= 3 && var.msk_broker_count % 2 == 1
    error_message = "MSK broker count must be an odd number of at least 3."
  }
}
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

resource "aws_cloudwatch_log_group" "application" {
  name              = "/taxflow360/${module.platform_contract.name}/application"
  retention_in_days = 30
  kms_key_id        = aws_kms_key.lakehouse.arn
  tags              = module.platform_contract.tags
}

resource "aws_cloudwatch_log_group" "audit" {
  name              = "/taxflow360/${module.platform_contract.name}/audit"
  retention_in_days = 2555
  kms_key_id        = aws_kms_key.lakehouse.arn
  tags              = module.platform_contract.tags
}

resource "aws_db_subnet_group" "aurora" {
  count      = var.enable_managed_data_plane ? 1 : 0
  name       = "${module.platform_contract.name}-aurora"
  subnet_ids = var.private_subnet_ids
  tags       = module.platform_contract.tags
}

resource "aws_rds_cluster" "aurora" {
  count                           = var.enable_managed_data_plane ? 1 : 0
  cluster_identifier              = "${module.platform_contract.name}-aurora"
  engine                          = "aurora-postgresql"
  engine_mode                     = "provisioned"
  database_name                   = "taxflow"
  db_subnet_group_name            = aws_db_subnet_group.aurora[0].name
  vpc_security_group_ids          = [var.data_security_group_id]
  storage_encrypted               = true
  kms_key_id                      = aws_kms_key.lakehouse.arn
  backup_retention_period         = 35
  deletion_protection             = var.environment == "prod"
  skip_final_snapshot             = false
  final_snapshot_identifier       = "${module.platform_contract.name}-final"
  enabled_cloudwatch_logs_exports = ["postgresql"]
  tags                            = module.platform_contract.tags
}

resource "aws_rds_cluster_instance" "aurora" {
  count               = var.enable_managed_data_plane ? 2 : 0
  identifier          = "${module.platform_contract.name}-aurora-${count.index + 1}"
  cluster_identifier  = aws_rds_cluster.aurora[0].id
  instance_class      = var.aurora_instance_class
  engine              = aws_rds_cluster.aurora[0].engine
  publicly_accessible = false
  tags                = module.platform_contract.tags
}

resource "aws_msk_configuration" "kafka" {
  count             = var.enable_managed_data_plane ? 1 : 0
  name              = "${module.platform_contract.name}-kafka"
  kafka_versions    = ["3.7.x"]
  server_properties = <<-PROPERTIES
    auto.create.topics.enable=false
    delete.topic.enable=false
    num.partitions=12
    default.replication.factor=3
    min.insync.replicas=2
  PROPERTIES
}

resource "aws_msk_cluster" "kafka" {
  count                  = var.enable_managed_data_plane ? 1 : 0
  cluster_name           = "${module.platform_contract.name}-kafka"
  kafka_version          = "3.7.x"
  number_of_broker_nodes = var.msk_broker_count
  broker_node_group_info {
    instance_type   = "kafka.m7g.large"
    client_subnets  = var.private_subnet_ids
    security_groups = [var.data_security_group_id]
    storage_info {
      ebs_storage_info {
        volume_size = 100
      }
    }
  }
  encryption_info {
    encryption_at_rest_kms_key_arn = aws_kms_key.lakehouse.arn
    encryption_in_transit {
      client_broker = "TLS"
      in_cluster    = true
    }
  }
  configuration_info {
    arn      = aws_msk_configuration.kafka[0].arn
    revision = aws_msk_configuration.kafka[0].latest_revision
  }
  logging_info {
    broker_logs {
      cloudwatch_logs {
        enabled   = true
        log_group = aws_cloudwatch_log_group.application.name
      }
    }
  }
  tags = module.platform_contract.tags
}

resource "aws_elasticache_subnet_group" "redis" {
  count      = var.enable_managed_data_plane ? 1 : 0
  name       = "${module.platform_contract.name}-redis"
  subnet_ids = var.private_subnet_ids
  tags       = module.platform_contract.tags
}

resource "aws_elasticache_replication_group" "redis" {
  count                      = var.enable_managed_data_plane ? 1 : 0
  replication_group_id       = "${module.platform_contract.name}-redis"
  description                = "TaxFlow cache; no source-of-truth data"
  node_type                  = var.redis_node_type
  num_cache_clusters         = 2
  engine                     = "redis"
  transit_encryption_enabled = true
  at_rest_encryption_enabled = true
  kms_key_id                 = aws_kms_key.lakehouse.arn
  subnet_group_name          = aws_elasticache_subnet_group.redis[0].name
  security_group_ids         = [var.data_security_group_id]
  automatic_failover_enabled = true
  multi_az_enabled           = true
  tags                       = module.platform_contract.tags
}

output "aurora_endpoint" {
  value = try(aws_rds_cluster.aurora[0].endpoint, null)
}
output "kafka_bootstrap_brokers_tls" {
  value = try(aws_msk_cluster.kafka[0].bootstrap_brokers_tls, null)
}
output "redis_primary_endpoint" {
  value = try(aws_elasticache_replication_group.redis[0].primary_endpoint_address, null)
}
