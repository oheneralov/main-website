# Development Environment Variables
# Usage: terraform apply -var-file="environments/dev.tfvars"

region                = "us-east-1"
environment           = "dev"
cluster_name          = "aws-info-website-dev"
kubernetes_namespace  = "development"

helm_chart_path       = "../helm-dir"
helm_release_name     = "mainwebsite"
helm_timeout          = 300
helm_atomic_deployment = true

mainwebsite_image_tag = "dev-latest"
metrics_image_tag     = "dev-latest"

helm_set_values = {
  "mainwebsite.replicaCount" = "1"
  "metrics.replicaCount"     = "1"
}

common_labels = {
  environment = "dev"
  managed_by  = "terraform"
  project     = "aws-info-website"
  team        = "platform"
}

terraform_state_bucket = "tf-state-dev-your-account-id"
terraform_state_key    = "aws-info-website/terraform/dev"
