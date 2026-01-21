# Development Environment Variables
# Usage: terraform apply -var-file="environments/dev.tfvars"

# AWS Configuration
region                   = "us-east-1"
environment              = "dev"

# EKS Cluster Configuration
cluster_name       = "aws_info_website_dev"
kubernetes_version = "1.30"

# VPC/Network Configuration (replace with your subnet IDs)
# Get your subnet IDs from your VPC configuration
subnet_ids = [
  "subnet-ccb26981", # us-east-1a
  "subnet-f96e7aa5"  # us-east-1b
]

# Optional: Security Groups (leave empty for default)
cluster_security_group_ids = []

# Cluster endpoint access (auto-detects caller IP when CIDRs left empty)
cluster_endpoint_public_access       = true
cluster_endpoint_public_access_cidrs = ["212.180.201.92/32"]

# Cluster logging
cluster_log_types = ["api", "audit", "authenticator"]

# Node Group Configuration
node_group_min_size     = 1
node_group_max_size     = 3
node_group_desired_size = 2
node_instance_types     = ["t2.small"]
node_disk_size          = 50

# Kubernetes & Helm Configuration
kubernetes_namespace   = "development"
helm_chart_path        = "../helm-dir"
helm_release_name      = "mainwebsite"
helm_timeout           = 1200
helm_atomic_deployment = true

# CRD Installation
install_traefik_crds = true
traefik_crd_version  = "30.0.0"

mainwebsite_image_tag = "dev-latest"

helm_set_values = {
  "mainwebsite.replicaCount" = "1"
}

# S3 Configuration
s3_bucket_name        = "aws-info-website-dev-data"
s3_versioning_enabled = true

# State Management
terraform_state_bucket = "tf-state-dev-your-account-id"
terraform_state_key    = "aws_info_website_terraform_dev"

# Tags
common_labels = {
  environment = "dev"
  managed_by  = "terraform"
  project     = "aws-info-website"
  team        = "platform"
}

deploy_kubernetes_manifests = false

