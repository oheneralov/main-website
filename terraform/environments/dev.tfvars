# Development Environment Variables
# Usage: terraform apply -var-file="environments/dev.tfvars"

# AWS Configuration
region                        = "us-east-1"
environment                   = "dev"

# EKS Cluster Configuration
create_cluster                = true
cluster_name                  = "aws-info-website-dev"
kubernetes_version            = "1.28"

# VPC/Network Configuration (replace with your subnet IDs)
# Get your subnet IDs from your VPC configuration
subnet_ids                    = [
  "subnet-xxxxxxxx",  # Replace with your private subnet 1
  "subnet-yyyyyyyy"   # Replace with your private subnet 2
]

# Optional: Security Groups (leave empty for default)
cluster_security_group_ids    = []

# Cluster endpoint access
cluster_endpoint_public_access          = true
cluster_endpoint_public_access_cidrs    = ["0.0.0.0/0"]  # Restrict this in production!

# Cluster logging
cluster_log_types             = ["api", "audit", "authenticator"]

# Node Group Configuration
node_group_min_size           = 1
node_group_max_size           = 3
node_group_desired_size       = 2
node_instance_types           = ["t3.medium"]
node_disk_size                = 50

# Kubernetes & Helm Configuration
kubernetes_namespace          = "development"
helm_chart_path               = "../helm-dir"
helm_release_name             = "mainwebsite"
helm_timeout                  = 300
helm_atomic_deployment        = true

mainwebsite_image_tag         = "dev-latest"
metrics_image_tag             = "dev-latest"

helm_set_values = {
  "mainwebsite.replicaCount" = "1"
  "metrics.replicaCount"     = "1"
}

# State Management
terraform_state_bucket        = "your-terraform-state-bucket-dev"
terraform_state_key           = "aws-info-website/dev/terraform.tfstate"

# Tags
common_labels = {
  managed_by  = "terraform"
  project     = "aws-info-website"
  environment = "dev"
}

common_labels = {
  environment = "dev"
  managed_by  = "terraform"
  project     = "aws-info-website"
  team        = "platform"
}

terraform_state_bucket = "tf-state-dev-your-account-id"
terraform_state_key    = "aws-info-website/terraform/dev"
