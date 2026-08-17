variable "certification_run_id" { type = string, validation { condition = can(regex("^[a-f0-9-]{16,64}$",var.certification_run_id)); error_message = "run ID must be explicit and safe" } }
variable "candidate_sha" { type = string, validation { condition = can(regex("^[a-f0-9]{40,64}$",var.candidate_sha)); error_message = "candidate SHA is required" } }
variable "cloud" { type = string, validation { condition = contains(["aws","azure","gcp"],var.cloud); error_message = "cloud must be aws, azure or gcp" } }
variable "region" { type = string }
variable "ttl_hours" { type = number, default = 8, validation { condition = var.ttl_hours>=1 && var.ttl_hours<=24; error_message = "TTL must be 1..24 hours" } }
variable "max_budget" { type = number, validation { condition = var.max_budget>0 && var.max_budget<=1000; error_message = "budget must be approved and <=1000" } }
variable "apply_approved" { type = bool, default = false }
