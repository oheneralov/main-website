################################################################################
# Helm Provider Configuration and Deployment
################################################################################
# This file manages Helm provider configuration and chart deployments
# Separates Helm-specific configuration from other infrastructure

################################################################################
# Helm Provider
################################################################################

provider "helm" {
  kubernetes {
    host                   = data.aws_eks_cluster.cluster.endpoint
    cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority[0].data)
    token                  = data.aws_eks_cluster_auth.cluster.token
  }
}

################################################################################
# Create Kubernetes Namespace
################################################################################

resource "kubernetes_namespace" "helm_namespace" {
  metadata {
    name   = var.kubernetes_namespace
    labels = merge(
      var.common_labels,
      {
        "name" = var.kubernetes_namespace
      }
    )
  }

  depends_on = [
    data.aws_eks_cluster.cluster
  ]
}

################################################################################
# Main Website Helm Release
################################################################################

resource "helm_release" "mainwebsite" {
  name             = var.helm_release_name
  chart            = var.helm_chart_path
  namespace        = kubernetes_namespace.helm_namespace.metadata[0].name
  version          = var.helm_chart_version
  create_namespace = false # We explicitly created the namespace above

  # Load values from file
  values = [
    file("${var.helm_chart_path}/values.yaml")
  ]

  # Environment-specific values override
  values_files = var.helm_values_files

  # Additional inline values
  dynamic "values" {
    for_each = var.helm_inline_values
    content {
      values = [values.value]
    }
  }

  # Individual set values (takes precedence over values files)
  dynamic "set" {
    for_each = local.helm_set_values
    content {
      name  = set.key
      value = set.value
    }
  }

  # Complex object values (from set_sensitive for secrets)
  dynamic "set" {
    for_each = var.helm_set_sensitive_values
    content {
      name      = set.key
      value     = set.value
      sensitive = true
    }
  }

  # Timeouts
  timeout = var.helm_timeout

  # Atomic deployments (rollback on failure)
  atomic = var.helm_atomic_deployment

  # Max history
  max_history = var.helm_max_history

  # Wait for resources to be ready
  wait = var.helm_wait
  wait_for_jobs = var.helm_wait_for_jobs

  # Recreate pods if necessary
  recreate_pods = var.helm_recreate_pods

  # Force upgrade
  force_update = var.helm_force_update

  # Cleanup on fail
  cleanup_on_fail = var.helm_cleanup_on_fail

  # Debug mode
  debug = var.helm_debug

  depends_on = [
    kubernetes_namespace.helm_namespace,
    data.aws_eks_cluster.cluster
  ]
}

################################################################################
# Service Account for Helm Operations (Optional but recommended)
################################################################################

resource "kubernetes_service_account" "helm_service_account" {
  count = var.create_helm_service_account ? 1 : 0

  metadata {
    name      = "${var.helm_release_name}-sa"
    namespace = kubernetes_namespace.helm_namespace.metadata[0].name
    labels    = merge(
      var.common_labels,
      {
        "helm-release" = var.helm_release_name
      }
    )
  }

  depends_on = [kubernetes_namespace.helm_namespace]
}
