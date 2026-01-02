# Staging Environment Variables
# Usage: terraform apply -var-file="environments/staging.tfvars"

region                = "us-east-1"
environment           = "staging"
cluster_name          = "aws-info-website-staging"
kubernetes_namespace  = "staging"

helm_chart_path       = "../helm-dir"
helm_release_name     = "mainwebsite"
helm_timeout          = 300
helm_atomic_deployment = true

mainwebsite_image_tag = "staging-latest"
metrics_image_tag     = "staging-latest"

helm_set_values = {
  "mainwebsite.replicaCount" = "2"
  "metrics.replicaCount"     = "1"
  "mainwebsite.autoscaling.enabled" = "true"
  "mainwebsite.autoscaling.maxReplicas" = "4"
}

common_labels = {
  environment = "staging"
  managed_by  = "terraform"
  project     = "aws-info-website"
  team        = "platform"
}

terraform_state_bucket = "tf-state-staging-your-account-id"
terraform_state_key    = "aws-info-website/terraform/staging"
