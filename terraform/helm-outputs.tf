################################################################################
# Helm Release Outputs
################################################################################

################################################################################
# Helm Release Status Outputs
################################################################################

output "helm_release_id" {
  description = "Helm release ID"
  value       = length(helm_release.mainwebsite) > 0 ? helm_release.mainwebsite[0].id : null
}

output "helm_release_name" {
  description = "Name of the Helm release"
  value       = length(helm_release.mainwebsite) > 0 ? helm_release.mainwebsite[0].name : null
}

output "helm_release_namespace" {
  description = "Kubernetes namespace where Helm release is deployed"
  value       = length(helm_release.mainwebsite) > 0 ? helm_release.mainwebsite[0].namespace : null
}

output "helm_release_status" {
  description = "Status of the Helm release (deployed, failed, superseded, etc.)"
  value       = length(helm_release.mainwebsite) > 0 ? helm_release.mainwebsite[0].status : null
}

output "helm_release_version" {
  description = "Version of the deployed Helm chart"
  value       = length(helm_release.mainwebsite) > 0 ? helm_release.mainwebsite[0].version : null
}

output "helm_chart_name" {
  description = "Name of the Helm chart"
  value       = length(helm_release.mainwebsite) > 0 ? helm_release.mainwebsite[0].chart : null
}

################################################################################
# Helm Release Configuration Outputs
################################################################################

output "helm_manifest" {
  description = "Helm release manifest (rendered Kubernetes resources)"
  value       = length(helm_release.mainwebsite) > 0 ? helm_release.mainwebsite[0].manifest : null
  sensitive   = true
}

output "helm_values" {
  description = "Computed Helm values used for the release"
  value = {
    set_values         = local.helm_set_values
    environment_config = local.env_config
    image_tags = {
      mainwebsite = var.mainwebsite_image_tag
    }
  }
  sensitive = true
}

################################################################################
# Kubernetes Namespace Outputs
################################################################################

output "kubernetes_namespace_name" {
  description = "Name of the Kubernetes namespace created for Helm release"
  value       = length(kubernetes_namespace.helm_namespace) > 0 ? kubernetes_namespace.helm_namespace[0].metadata[0].name : null
}

output "kubernetes_namespace_uid" {
  description = "UID of the Kubernetes namespace"
  value       = length(kubernetes_namespace.helm_namespace) > 0 ? kubernetes_namespace.helm_namespace[0].metadata[0].uid : null
}

################################################################################
# Service Account Outputs
################################################################################

output "helm_service_account_name" {
  description = "Name of the service account for Helm operations"
  value       = try(kubernetes_service_account.helm_service_account[0].metadata[0].name, null)
}

output "helm_service_account_namespace" {
  description = "Namespace of the service account for Helm operations"
  value       = try(kubernetes_service_account.helm_service_account[0].metadata[0].namespace, null)
}

################################################################################
# Helm Deployment Configuration Summary
################################################################################

output "helm_deployment_summary" {
  description = "Summary of Helm deployment configuration"
  value = {
    release_name       = var.helm_release_name
    namespace          = var.kubernetes_namespace
    chart_path         = var.helm_chart_path
    chart_version      = var.helm_chart_version != "" ? var.helm_chart_version : "default (from Chart.yaml)"
    timeout_seconds    = local.helm_timeout_final
    atomic_deployment  = var.helm_atomic_deployment
    wait_for_resources = var.helm_wait
    max_history        = var.helm_max_history
    environment        = var.environment
  }
}

################################################################################
# Commands for Manual Helm Operations
################################################################################

output "helm_commands" {
  description = "Useful Helm CLI commands for manual operations"
  value = {
    status         = "helm status ${var.helm_release_name} -n ${var.kubernetes_namespace}"
    values         = "helm get values ${var.helm_release_name} -n ${var.kubernetes_namespace}"
    manifest       = "helm get manifest ${var.helm_release_name} -n ${var.kubernetes_namespace}"
    history        = "helm history ${var.helm_release_name} -n ${var.kubernetes_namespace}"
    rollback       = "helm rollback ${var.helm_release_name} 1 -n ${var.kubernetes_namespace}"
    delete         = "helm delete ${var.helm_release_name} -n ${var.kubernetes_namespace}"
    list_all       = "helm list -A"
    list_namespace = "helm list -n ${var.kubernetes_namespace}"
  }
}

################################################################################
# Verification Commands
################################################################################

output "verification_commands" {
  description = "kubectl commands to verify the Helm deployment"
  value = {
    check_pods         = "kubectl get pods -n ${var.kubernetes_namespace} -l app=${var.helm_release_name}"
    check_services     = "kubectl get svc -n ${var.kubernetes_namespace}"
    check_deployments  = "kubectl get deployments -n ${var.kubernetes_namespace}"
    describe_namespace = "kubectl describe namespace ${var.kubernetes_namespace}"
    check_events       = "kubectl get events -n ${var.kubernetes_namespace} --sort-by='.lastTimestamp'"
    tail_logs          = "kubectl logs -n ${var.kubernetes_namespace} -l app=${var.helm_release_name} -f"
  }
}
