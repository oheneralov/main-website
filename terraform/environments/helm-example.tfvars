################################################################################
# Helm Integration Example Configuration
# Copy this file and customize for your environment
#
# Usage:
# terraform apply -var-file="environments/helm-example.tfvars"
################################################################################

################################################################################
# AWS Configuration
################################################################################
region = "us-east-1"

################################################################################
# Environment
################################################################################
environment = "dev"

################################################################################
# EKS Cluster Configuration
################################################################################
cluster_name       = "my-info-website-cluster"
kubernetes_version = "1.28"

# Replace with your actual subnet IDs
subnet_ids = [
  "subnet-12345678",
  "subnet-87654321"
]

node_instance_types     = ["t3.medium"]
node_group_min_size     = 1
node_group_max_size     = 3
node_group_desired_size = 2
node_disk_size          = 20

################################################################################
# Kubernetes Namespace
################################################################################
kubernetes_namespace = "production"

################################################################################
# Helm Release Configuration
################################################################################

# Chart configuration
helm_chart_path    = "../helm-dir"
helm_chart_version = "" # Empty = use version in Chart.yaml
helm_release_name  = "mainwebsite"

################################################################################
# Helm Deployment Behavior
################################################################################

# Timeouts and retry behavior
helm_timeout           = 300   # 5 minutes
helm_atomic_deployment = true  # Rollback on failure
helm_wait              = true  # Wait for resources to be ready
helm_wait_for_jobs     = false # Don't wait for Kubernetes jobs
helm_max_history       = 10    # Keep 10 release revisions
helm_recreate_pods     = false # Don't recreate pods on change
helm_force_update      = false # Don't force update
helm_cleanup_on_fail   = true  # Clean up on failure
helm_debug             = false # Disable debug logging

################################################################################
# Helm Values - Individual Set Values
################################################################################

helm_set_values = {
  # Replica counts (automatically set by locals based on environment)
  # "mainwebsite.replicaCount"        = "1"

  # Image tags (set via dedicated variables below)
  # "mainwebsite.image.tag"           = "latest"

  # Enable/disable components
  "mainwebsite.autoscaling.enabled" = "false"

  # Custom settings
  # "mainwebsite.service.type"        = "LoadBalancer"
}

################################################################################
# Helm Sensitive Values (use for secrets, API keys, etc.)
################################################################################

helm_set_sensitive_values = {
  # "apiKey"          = "your-api-key"     # Commented out for security
}

################################################################################
# Helm Values Files
################################################################################

# List of values files to merge (in order of precedence)
# Files are automatically merged with later files overriding earlier ones
helm_values_files = [
  # Environment-specific values are automatically included from:
  # "../helm-dir/values-${var.environment}.yaml"
  # "../helm-dir/values-dev.yaml"
]

################################################################################
# Docker Image Tags
################################################################################

mainwebsite_image_tag = "latest"

################################################################################
# Helm Repository Configuration (for remote charts - optional)
################################################################################

helm_repository_url      = "" # Empty = use local chart path
helm_repository_username = "" # For private repositories
helm_repository_password = "" # For private repositories

################################################################################
# Helm Service Account
################################################################################

create_helm_service_account = false # Set to true if using RBAC

################################################################################
# Common Labels and Tags
################################################################################

common_labels = {
  managed_by  = "terraform"
  project     = "aws-info-website"
  environment = "dev"
}

################################################################################
# Terraform State Configuration
################################################################################

terraform_state_bucket = "my-terraform-state-bucket"
terraform_state_key    = "aws-info-website/terraform"
