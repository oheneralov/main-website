################################################################################
# AWS & Kubernetes Cluster Outputs
################################################################################

output "aws_region" {
  description = "The AWS region"
  value       = var.region
}

output "eks_cluster_name" {
  description = "Name of the EKS cluster"
  value       = local.eks_cluster_name
}

output "eks_cluster_endpoint" {
  description = "EKS cluster endpoint (Kubernetes API server address)"
  value       = local.eks_cluster_endpoint
  sensitive   = true
}

output "eks_cluster_ca_certificate" {
  description = "EKS cluster CA certificate (for kubectl configuration)"
  value       = local.eks_cluster_ca_data
  sensitive   = true
}

output "eks_cluster_arn" {
  description = "The Amazon Resource Name (ARN) of the EKS cluster"
  value       = local.eks_cluster_arn
}

output "eks_cluster_status" {
  description = "Status of the EKS cluster"
  value       = aws_eks_cluster.main.status
}

output "eks_cluster_version" {
  description = "Kubernetes version of the EKS cluster"
  value       = aws_eks_cluster.main.version
}

output "eks_node_group_id" {
  description = "EKS node group ID"
  value       = aws_eks_node_group.main.id
}

output "eks_node_group_status" {
  description = "Status of the EKS node group"
  value       = aws_eks_node_group.main.status
}

output "eks_cluster_role_arn" {
  description = "ARN of the EKS cluster IAM role"
  value       = aws_iam_role.eks_cluster_role.arn
}

output "eks_node_role_arn" {
  description = "ARN of the EKS node IAM role"
  value       = aws_iam_role.eks_node_role.arn
}

################################################################################
# Application Deployment Information
################################################################################

output "environment" {
  description = "Deployment environment (dev)"
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

################################################################################
# Useful Commands & Information
################################################################################

output "kubectl_configure_command" {
  description = "Command to configure kubectl context"
  value       = "aws eks update-kubeconfig --name ${local.eks_cluster_name} --region ${var.region}"
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
  value       = length(helm_release.mainwebsite) > 0 ? "kubectl logs -n ${var.kubernetes_namespace} -l app.kubernetes.io/instance=${helm_release.mainwebsite[0].name}" : ""
}
