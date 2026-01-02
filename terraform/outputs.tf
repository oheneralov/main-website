################################################################################
# AWS & Kubernetes Cluster Outputs
################################################################################

output "aws_region" {
  description = "The AWS region"
  value       = var.region
}

output "eks_cluster_name" {
  description = "Name of the EKS cluster"
  value       = data.aws_eks_cluster.cluster.name
}

output "eks_cluster_endpoint" {
  description = "EKS cluster endpoint (Kubernetes API server address)"
  value       = data.aws_eks_cluster.cluster.endpoint
  sensitive   = true
}

output "eks_cluster_ca_certificate" {
  description = "EKS cluster CA certificate (for kubectl configuration)"
  value       = data.aws_eks_cluster.cluster.certificate_authority[0].data
  sensitive   = true
}

output "eks_cluster_arn" {
  description = "The Amazon Resource Name (ARN) of the EKS cluster"
  value       = data.aws_eks_cluster.cluster.arn
}

################################################################################
# Helm Release Outputs
################################################################################

output "helm_release_name" {
  description = "Name of the deployed Helm release"
  value       = helm_release.mainwebsite.name
}

output "helm_release_namespace" {
  description = "Kubernetes namespace of the Helm release"
  value       = helm_release.mainwebsite.namespace
}

output "helm_release_status" {
  description = "Status of the Helm release"
  value       = helm_release.mainwebsite.status
}

output "helm_release_version" {
  description = "Version of the deployed Helm chart"
  value       = helm_release.mainwebsite.version
}

################################################################################
# Application Deployment Information
################################################################################

output "environment" {
  description = "Deployment environment (dev, staging, production)"
  value       = var.environment
}

output "application_namespace" {
  description = "Kubernetes namespace where the application is deployed"
  value       = var.kubernetes_namespace
}

output "mainwebsite_image_tag" {
  description = "Docker image tag for mainwebsite service"
  value       = var.mainwebsite_image_tag
}

output "metrics_image_tag" {
  description = "Docker image tag for metrics service"
  value       = var.metrics_image_tag
}

################################################################################
# Useful Commands & Information
################################################################################

output "kubectl_configure_command" {
  description = "Command to configure kubectl context"
  value       = "aws eks update-kubeconfig --name ${data.aws_eks_cluster.cluster.name} --region ${var.region}"
}

output "helm_list_command" {
  description = "Command to list Helm releases"
  value       = "helm list -n ${var.kubernetes_namespace}"
}

output "kubectl_get_pods_command" {
  description = "Command to get pods in the application namespace"
  value       = "kubectl get pods -n ${var.kubernetes_namespace}"
}

output "kubectl_logs_command" {
  description = "Command to view application logs"
  value       = "kubectl logs -n ${var.kubernetes_namespace} -l app.kubernetes.io/instance=${helm_release.mainwebsite.name}"
}

################################################################################
# Debug Information (comment out for production)
################################################################################

# output "gcp_client_config" {
#   description = "Google Cloud client configuration (for debugging)"
#   value = {
#     project = data.google_client_config.default.project
#     region  = data.google_client_config.default.region
#     zone    = data.google_client_config.default.zone
#   }
# }
