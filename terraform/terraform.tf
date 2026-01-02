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

# Note: Kubernetes and Helm provider configuration is in main.tf
# They are configured to work with AWS EKS clusters (either new or existing)
