run "platform_contract" {
  command = plan
  module { source = "../modules/platform" }
  variables {
    environment = "staging"
    region = "southamerica-east1"
    data_residency = "BR"
    databricks_workspace_url = "https://example.cloud.databricks.com"
    tags = { owner = "platform-engineering" }
  }
  assert {
    condition     = output.name == "taxflow360-staging"
    error_message = "Naming contract drifted."
  }
  assert {
    condition     = output.tags.managed_by == "terraform"
    error_message = "Mandatory ownership tag is absent."
  }
  assert {
    condition     = output.tags.data_residency == "BR"
    error_message = "Residency classification is absent."
  }
}
