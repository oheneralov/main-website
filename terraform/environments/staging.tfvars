# Staging Environment Variables
# Usage: terraform apply -var-file="environments/staging.tfvars"

# AWS Configuration
region                        = "us-east-1"
environment                   = "staging"

# EKS Cluster Configuration
create_cluster                = true
cluster_name                  = "aws-info-website-staging"
kubernetes_version            = "1.28"

# VPC/Network Configuration (replace with your subnet IDs)
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
cluster_log_types             = ["api", "audit", "authenticator", "controllerManager"]

# Node Group Configuration
node_group_min_size           = 2
node_group_max_size           = 5
node_group_desired_size       = 3
node_instance_types           = ["t3.medium"]
node_disk_size                = 50

# Kubernetes & Helm Configuration
kubernetes_namespace          = "staging"
helm_chart_path               = "../helm-dir"
helm_release_name             = "mainwebsite"
helm_timeout                  = 300
helm_atomic_deployment        = true

mainwebsite_image_tag         = "staging-latest"
metrics_image_tag             = "staging-latest"

helm_set_values = {
  "mainwebsite.replicaCount"           = "2"
  "metrics.replicaCount"               = "1"
  "mainwebsite.autoscaling.enabled"    = "true"
  "mainwebsite.autoscaling.maxReplicas" = "4"
}

# State Management
terraform_state_bucket        = "your-terraform-state-bucket-staging"
terraform_state_key           = "aws-info-website/staging/terraform.tfstate"

# Tags
common_labels = {
  environment = "staging"
  managed_by  = "terraform"
  project     = "aws-info-website"
  team        = "platform"
}
terraform_state_key    = "aws-info-website/terraform/staging"
