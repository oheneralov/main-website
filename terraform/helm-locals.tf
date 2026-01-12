################################################################################
# Helm Local Values - Computed values for Helm operations
################################################################################

locals {
  ################################################################################
  # Helm Set Values - Processed and environment-specific
  ################################################################################
  
  # Base set values with environment-specific overrides
  helm_set_values = merge(
    var.helm_set_values,
    local.environment_specific_helm_values
  )

  ################################################################################
  # Environment-Specific Helm Values
  ################################################################################
  
  environment_specific_helm_values = {
    "mainwebsite.replicaCount"        = local.env_config.replica_count_main
    "metrics.replicaCount"            = local.env_config.replica_count_metrics
    "mainwebsite.image.tag"           = var.mainwebsite_image_tag
    "metrics.image.tag"               = var.metrics_image_tag
    "mainwebsite.autoscaling.enabled" = local.env_config.enable_monitoring ? "true" : "false"
  }

  ################################################################################
  # Helm Chart Reference
  ################################################################################
  
  # Full chart reference for remote repositories
  helm_chart_ref = var.helm_chart_repository != "" ? "${var.helm_chart_repository}/${var.helm_chart_namespace}/${var.helm_release_name}" : var.helm_chart_path

  ################################################################################
  # Helm Values Files for Current Environment
  ################################################################################
  
  # Automatically include environment-specific values if they exist
  helm_values_files_computed = concat(
    var.helm_values_files,
    [
      # Add environment-specific values file if it exists
      # Format: values-{environment}.yaml in helm chart directory
      var.kubernetes_namespace != "" ? 
        "${var.helm_chart_path}/values-${var.environment}.yaml" : 
        ""
    ]
  )

  # Filter out empty strings
  helm_values_files_filtered = [
    for file in local.helm_values_files_computed : file
    if file != ""
  ]

  ################################################################################
  # Helm Release Naming and Metadata
  ################################################################################
  
  helm_release_metadata = {
    name      = var.helm_release_name
    namespace = var.kubernetes_namespace
    chart     = local.helm_chart_ref
    version   = var.helm_chart_version != "" ? var.helm_chart_version : null
  }

  ################################################################################
  # Helm Rollback/History Configuration
  ################################################################################
  
  helm_history_config = {
    max_history = var.helm_max_history
    atomic      = var.helm_atomic_deployment
    cleanup_on_fail = var.helm_cleanup_on_fail
  }

  ################################################################################
  # Helm Timeout Configuration (based on environment)
  ################################################################################
  
  helm_timeout_computed = {
    dev         = var.helm_timeout
    staging     = var.helm_timeout + 60  # Slightly higher for staging
    production  = var.helm_timeout + 120 # Higher timeout for production
  }

  # Use environment-specific timeout, fallback to configured timeout
  helm_timeout_final = try(local.helm_timeout_computed[var.environment], var.helm_timeout)
}
