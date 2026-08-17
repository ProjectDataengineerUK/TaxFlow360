terraform { required_version = ">= 1.7.0" }
locals {
  name   = "taxflow-cert-${var.cloud}-${substr(var.certification_run_id, 0, 12)}"
  labels = { purpose = "certification", candidate = var.candidate_sha, ttl_hours = tostring(var.ttl_hours), synthetic_data_only = "true" }
}
resource "terraform_data" "certification_contract" {
  input = { name = local.name, cloud = var.cloud, region = var.region, labels = local.labels, max_budget = var.max_budget, apply_approved = var.apply_approved }
  lifecycle {
    precondition {
      condition     = !var.apply_approved || var.max_budget <= 1000
      error_message = "apply requires bounded approved budget"
    }
  }
}
