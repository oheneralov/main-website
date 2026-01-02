terraform {
  # Required version constraint for Terraform
  required_version = ">= 1.0"

  # Required providers with explicit versions
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.20"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.10"
    }
  }

  # Remote state management in Amazon S3
  # S3 with DynamoDB provides state locking
  # Backend configuration is provided via:
  # - Backend config file: terraform init -backend-config=backend-config.tfvars
  # - Command line flags: terraform init -backend-config="bucket=..." -backend-config="key=..."
  # - Environment file in each environment directory (dev.tfvars, staging.tfvars, production.tfvars)
  backend "s3" {
    # Bucket and key are configured via backend-config during init
    # Example: terraform init -backend-config="bucket=tf-state-bucket-name" -backend-config="key=aws-info-website/terraform"
    # Uncomment below for DynamoDB state locking:
    # dynamodb_table = "terraform-locks"
  }
}

# AWS Provider Configuration
# Credentials are sourced from AWS credentials file or environment variables
# Set it via: export AWS_ACCESS_KEY_ID="..." AWS_SECRET_ACCESS_KEY="..." (Unix/Linux/macOS)
#       or: $env:AWS_ACCESS_KEY_ID="..."; $env:AWS_SECRET_ACCESS_KEY="..." (PowerShell)
# Or configure via AWS CLI: aws configure
provider "aws" {
  region = var.region

  default_tags {
    tags = {
      managed_by  = "terraform"
      environment = var.environment
      project     = "aws-info-website"
    }
  }
}

# Kubernetes Provider Configuration
provider "kubernetes" {
  host  = "https://${data.google_container_cluster.gke.endpoint}"
  token = data.google_client_config.default.access_token

  cluster_ca_certificate = base64decode(
    data.google_container_cluster.gke.master_auth[0].cluster_ca_certificate
  )
}

# Helm Provider Configuration
provider "helm" {
  kubernetes {
    host  = "https://${data.google_container_cluster.gke.endpoint}"
    token = data.google_client_config.default.access_token

    cluster_ca_certificate = base64decode(
      data.google_container_cluster.gke.master_auth[0].cluster_ca_certificate
    )
  }
}

# Retrieve active Google Cloud client configuration
data "google_client_config" "default" {}

# Retrieve existing GKE cluster details
data "google_container_cluster" "gke" {
  name       = var.cluster_name
  location   = var.region
  project    = var.project_id
}

# Deploy mainwebsite Helm chart
resource "helm_release" "mainwebsite" {
  name             = local.helm_release_name
  namespace        = var.kubernetes_namespace
  create_namespace = true
  chart            = var.helm_chart_path
  timeout          = var.helm_timeout
  wait             = true
  wait_for_jobs    = true
  atomic           = var.helm_atomic_deployment

  # Use environment-specific values file
  values = [
    templatefile("${var.helm_chart_path}/values.yaml", {}),
    templatefile("${var.helm_chart_path}/values-${var.environment}.yaml", {})
  ]

  # Override specific chart values
  set {
    name  = "image.mainwebsite.tag"
    value = var.mainwebsite_image_tag
  }

  set {
    name  = "image.metrics.tag"
    value = var.metrics_image_tag
  }

  set {
    name  = "global.namespace"
    value = var.kubernetes_namespace
  }

  # Add labels and annotations for tracking
  dynamic "set" {
    for_each = var.helm_set_values
    content {
      name  = set.key
      value = set.value
    }
  }

  depends_on = [
    data.google_container_cluster.gke
  ]

  lifecycle {
    ignore_changes = [
      version
    ]
  }
}
