# Production Environment Variables
# Usage: terraform apply -var-file="environments/production.tfvars"
# IMPORTANT: Treat this file as sensitive - consider using remote state or Terraform Cloud

# AWS Configuration
region                        = "us-east-1"
environment                   = "production"

# EKS Cluster Configuration
create_cluster                = true
cluster_name                  = "aws-info-website-prod"
kubernetes_version            = "1.28"

# VPC/Network Configuration (replace with your subnet IDs)
# PRODUCTION: Use multiple subnets across different AZs for high availability
subnet_ids                    = [
  "subnet-xxxxxxxx",  # Replace with your private subnet 1 (AZ-a)
  "subnet-yyyyyyyy",  # Replace with your private subnet 2 (AZ-b)
  "subnet-zzzzzzzz"   # Replace with your private subnet 3 (AZ-c)
]

# Optional: Security Groups (leave empty for default)
cluster_security_group_ids    = []

# Cluster endpoint access
cluster_endpoint_public_access          = true
cluster_endpoint_public_access_cidrs    = ["0.0.0.0/0"]  # PRODUCTION: Restrict to known IPs!

# Cluster logging - Enable all logging in production
cluster_log_types             = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

# Node Group Configuration - HA Setup
node_group_min_size           = 3
node_group_max_size           = 20
node_group_desired_size       = 5
node_instance_types           = ["t3.large", "t3a.large"]  # Multiple types for cost optimization
node_disk_size                = 100

# Kubernetes & Helm Configuration
kubernetes_namespace          = "production"
helm_chart_path               = "../helm-dir"
helm_release_name             = "mainwebsite"
helm_timeout                  = 600
helm_atomic_deployment        = true

# Use explicit version tags in production, never "latest"
mainwebsite_image_tag         = "1.0.0"
metrics_image_tag             = "1.0.0"

helm_set_values = {
  "mainwebsite.replicaCount"               = "3"
  "metrics.replicaCount"                   = "2"
  "mainwebsite.autoscaling.enabled"        = "true"
  "mainwebsite.autoscaling.minReplicas"    = "3"
  "mainwebsite.autoscaling.maxReplicas"    = "10"
  "metrics.autoscaling.enabled"            = "true"
  "metrics.autoscaling.maxReplicas"        = "5"
  "monitoring.serviceMonitor.enabled"      = "true"
}

# State Management
terraform_state_bucket        = "your-terraform-state-bucket-prod"
terraform_state_key           = "aws-info-website/prod/terraform.tfstate"

# Tags
common_labels = {
  environment = "production"
  managed_by  = "terraform"
  project     = "aws-info-website"
  team        = "platform"
  sla         = "high"
}
