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
    host                   = local.eks_cluster_endpoint
    cluster_ca_certificate = base64decode(local.eks_cluster_ca_data)

    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args = [
        "eks",
        "get-token",
        "--cluster-name", local.eks_cluster_name,
        "--region", var.region
      ]
    }
  }
}


################################################################################
# Create Kubernetes Namespace
################################################################################

resource "kubernetes_namespace" "helm_namespace" {
  count = var.deploy_kubernetes_manifests ? 1 : 0
  metadata {
    name = var.kubernetes_namespace
    labels = merge(
      var.common_labels,
      {
        "name" = var.kubernetes_namespace
      }
    )
  }

  depends_on = [aws_eks_cluster.main]
}

################################################################################
# Install Required CRDs
################################################################################

# Traefik CRDs (for IngressRoute)
resource "helm_release" "traefik_crds" {
  count      = var.install_traefik_crds && var.deploy_kubernetes_manifests ? 1 : 0
  name       = "traefik-crds"
  chart      = "traefik"
  version    = var.traefik_crd_version
  repository = "https://helm.traefik.io/traefik"
  namespace  = "kube-system"

  # Install only CRDs
  set {
    name  = "installCRDs"
    value = "true"
  }

  depends_on = [
    kubernetes_namespace.helm_namespace,
    aws_eks_cluster.main,
    aws_eks_node_group.main
  ]
}

# Prometheus Operator CRDs (needed for ServiceMonitor, PodMonitor, etc.)
resource "helm_release" "prometheus_crds" {
  count      = var.install_prometheus_crds && var.deploy_kubernetes_manifests ? 1 : 0
  name       = "prometheus-operator-crds"
  chart      = "prometheus-operator-crds"
  repository = "https://prometheus-community.github.io/helm-charts"
  namespace  = "kube-system"
  version    = var.prometheus_crd_chart_version != null ? var.prometheus_crd_chart_version : null

  depends_on = [
    kubernetes_namespace.helm_namespace,
    aws_eks_cluster.main,
    aws_eks_node_group.main
  ]
}



################################################################################
# Main Website Helm Release
################################################################################

resource "helm_release" "mainwebsite" {
  count            = var.deploy_kubernetes_manifests ? 1 : 0
  name             = var.helm_release_name
  chart            = var.helm_chart_path
  namespace        = length(kubernetes_namespace.helm_namespace) > 0 ? kubernetes_namespace.helm_namespace[0].metadata[0].name : var.kubernetes_namespace
  version          = var.helm_chart_version
  create_namespace = false # We explicitly created the namespace above

  # Load values from file
  values = concat(
    [file("${var.helm_chart_path}/values.yaml")],
    var.helm_values_files != null && length(var.helm_values_files) > 0 ? [for f in var.helm_values_files : file(f)] : [],
    var.helm_inline_values != null && length(var.helm_inline_values) > 0 ? var.helm_inline_values : []
  )

  # Individual set values (takes precedence over values files)
  dynamic "set" {
    for_each = local.helm_set_values
    content {
      name  = set.key
      value = set.value
    }
  }

  # Complex object values (from set_sensitive for secrets)
  dynamic "set_sensitive" {
    for_each = var.helm_set_sensitive_values
    content {
      name  = set_sensitive.key
      value = set_sensitive.value
    }
  }

  # Timeouts
  timeout = var.helm_timeout

  # Atomic deployments (rollback on failure)
  atomic = var.helm_atomic_deployment

  # Max history
  max_history = var.helm_max_history

  # Wait for resources to be ready
  wait          = var.helm_wait
  wait_for_jobs = var.helm_wait_for_jobs

  # Recreate pods if necessary
  recreate_pods = var.helm_recreate_pods

  # Force upgrade
  force_update = var.helm_force_update

  # Cleanup on fail
  cleanup_on_fail = var.helm_cleanup_on_fail

  depends_on = [
    kubernetes_namespace.helm_namespace,
    helm_release.traefik_crds,
    helm_release.prometheus_crds,
    aws_eks_cluster.main,
    aws_eks_node_group.main
  ]
}

################################################################################
# Service Account for Helm Operations (Optional but recommended)
################################################################################

resource "kubernetes_service_account" "helm_service_account" {
  count = var.create_helm_service_account && var.deploy_kubernetes_manifests ? 1 : 0

  metadata {
    name      = "${var.helm_release_name}-sa"
    namespace = length(kubernetes_namespace.helm_namespace) > 0 ? kubernetes_namespace.helm_namespace[0].metadata[0].name : var.kubernetes_namespace
    labels = merge(
      var.common_labels,
      {
        "helm-release" = var.helm_release_name
      }
    )
  }

  depends_on = [kubernetes_namespace.helm_namespace]
}
