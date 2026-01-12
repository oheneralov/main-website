# Example Terraform Configuration for Development Environment
# Copy this file to environments/dev.tfvars and customize for your setup

# ============================================================
# AWS Configuration
# ============================================================

# AWS region for EKS cluster
# Options: us-east-1, us-west-2, eu-west-1, ap-southeast-1, etc.
region = "us-east-1"

# Environment name (dev/staging/production)
environment = "dev"

# ============================================================
# EKS Cluster Configuration
# ============================================================

# Whether to create a new EKS cluster (true) or reference an existing one (false)
create_cluster = true

# EKS cluster name
cluster_name = "aws-info-website-dev"

# Kubernetes version
kubernetes_version = "1.28"

# VPC Subnet IDs for the EKS cluster (at least 2 required)
# Replace with your actual subnet IDs
subnet_ids = ["subnet-xxxxxxxx", "subnet-yyyyyyyy"]

# Security group IDs for the EKS cluster (optional)
cluster_security_group_ids = []

# Enable public access to the EKS cluster endpoint
cluster_endpoint_public_access = true

# CIDR blocks that can access the public EKS endpoint
cluster_endpoint_public_access_cidrs = ["0.0.0.0/0"]

# EKS cluster logging types to enable
cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

# ============================================================
# EKS Node Group Configuration
# ============================================================

# Node group scaling
node_group_min_size = 1
node_group_max_size = 3
node_group_desired_size = 2

# EC2 instance types for the node group
# Options: t3.medium, t3.large, m5.large, etc.
node_instance_types = ["t3.medium"]

# Disk size in GB for each node
node_disk_size = 50

# ============================================================
# Kubernetes Configuration
# ============================================================

# Kubernetes namespace where applications will be deployed
kubernetes_namespace = "development"

# ============================================================
# Helm Configuration
# ============================================================

# Path to Helm chart (relative to terraform directory)
helm_chart_path = "../helm-dir"

# Helm release name (how it appears in "helm list")
helm_release_name = "mainwebsite"

# Timeout for Helm release deployment (seconds)
# Increase if deployments are timing out
helm_timeout = 300

# Atomic deployment: rollback on failed deployment
helm_atomic_deployment = true

# Wait for resources to be ready before returning
helm_wait = true

# ============================================================
# Application Configuration
# ============================================================

# Image tags for services
# For development: use 'dev-latest' for continuous development
# For staging: use 'staging-latest' for testing
# For production: use specific versions like 'v1.0.0', never 'latest'

mainwebsite_image_tag = "dev-latest"
metrics_image_tag = "dev-latest"

# Additional Helm values to override in the chart
# These are set as --set flags in Helm
helm_set_values = {
  # Replica counts
  "mainwebsite.replicaCount"           = "1"
  "metrics.replicaCount"               = "1"

  # Resource requests (usually lower in dev)
  "mainwebsite.resources.requests.memory"    = "256Mi"
  "mainwebsite.resources.requests.cpu"       = "100m"
  "mainwebsite.resources.limits.memory"      = "512Mi"
  "mainwebsite.resources.limits.cpu"         = "500m"

  # Autoscaling disabled in dev
  "mainwebsite.autoscaling.enabled"   = "false"
  "metrics.autoscaling.enabled"       = "false"

  # Ingress configuration (adjust hostname for your environment)
  "ingress.enabled"                   = "true"
  "ingress.hosts[0].host"             = "dev.aws-info-website.local"
  "ingress.tls.enabled"               = "false"

  # Update strategy
  "mainwebsite.strategy.type"         = "RollingUpdate"
}

# ============================================================
# S3 Configuration
# ============================================================

# S3 bucket name for application data storage
s3_bucket_name = "aws-info-website-dev-data"

# Enable versioning on the S3 bucket
s3_versioning_enabled = true

# ============================================================
# Terraform State Management
# ============================================================

# S3 bucket for storing Terraform state
terraform_state_bucket = "aws-info-website-terraform-state"

# S3 key path for Terraform state files
terraform_state_key = "aws-info-website/dev/terraform.tfstate"

# ============================================================
# Labels
# ============================================================

# Common labels applied to all resources
common_labels = {
  environment = "dev"
  managed_by  = "terraform"
  project     = "aws-info-website"
  team        = "platform"
}

# ============================================================
# Development-Specific Notes
# ============================================================

# Development environment guidelines:
# - 1-2 nodes for resource efficiency
# - Minimal resource requests
# - No autoscaling
# - Latest development images
# - No TLS required
# - Minimal logging level

# Cost estimates for this configuration:
# - 2x t3.medium nodes (monthly): ~$60
# - EKS cluster (monthly): $72
# - Total monthly estimate: ~$132 (excluding storage/networking/data transfer)

# Next steps after applying this configuration:
# 1. Configure AWS credentials: aws configure
# 2. Run: terraform init -backend-config="bucket=aws-info-website-terraform-state"
# 3. Run: terraform apply -var-file="environments/dev.tfvars"
# 4. Configure kubectl: aws eks update-kubeconfig --region us-east-1 --name aws-info-website-dev
# 5. Verify deployment: kubectl get pods -n development
# 6. Access application: kubectl port-forward -n development svc/mainwebsite 8080:80
# 7. View logs: kubectl logs -n development -l app=mainwebsite
