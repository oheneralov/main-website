################################################################################
# Local Values - Computed and reusable values
################################################################################

locals {
  # Helm release naming
  helm_release_name = var.helm_release_name

  # Common naming pattern for all resources
  resource_prefix = "${local.helm_release_name}-${var.environment}"

  # Environment-specific configuration
  environment_config = {
    dev = {
      replica_count_main = 1
      enable_monitoring  = false
    }
  }

  # Select environment-specific config
  env_config = local.environment_config[var.environment]

  # Common labels for all resources
  common_labels = merge(
    var.common_labels,
    {
      environment = var.environment
      managed_by  = "terraform"
      created_at  = timestamp()
    }
  )

  # Helm values file paths
  helm_base_values_file = "${var.helm_chart_path}/values.yaml"
  helm_env_values_file  = "${var.helm_chart_path}/values-${var.environment}.yaml"

  # Deployment tracking
  deployment_metadata = {
    release_name      = local.helm_release_name
    namespace         = var.kubernetes_namespace
    chart_path        = var.helm_chart_path
    environment       = var.environment
    deployed_at       = timestamp()
    terraform_version = "~> 1.0"
  }
}
