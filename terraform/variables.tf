################################################################################
# AWS Configuration Variables
################################################################################

variable "region" {
  description = "The AWS region for resource deployment (e.g., us-east-1, eu-west-1)"
  type        = string
  default     = "us-east-1"
  nullable    = false

  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-[0-9]{1}$", var.region))
    error_message = "Region must be a valid AWS region format."
  }
}

################################################################################
# Environment Configuration
################################################################################

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  nullable    = false

  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be one of: dev, staging, production."
  }
}

################################################################################
# Kubernetes & EKS Configuration
################################################################################

variable "cluster_name" {
  description = "Name of the existing EKS cluster"
  type        = string
  nullable    = false

  validation {
    condition     = length(var.cluster_name) > 0 && length(var.cluster_name) <= 100
    error_message = "Cluster name must be between 1 and 100 characters."
  }
}

variable "kubernetes_namespace" {
  description = "Kubernetes namespace for deploying the application"
  type        = string
  default     = "default"
  nullable    = false

  validation {
    condition     = can(regex("^[a-z0-9]([-a-z0-9]*[a-z0-9])?$", var.kubernetes_namespace))
    error_message = "Namespace must be a valid Kubernetes namespace name."
  }
}

################################################################################
# Helm Chart Configuration
################################################################################

variable "helm_chart_path" {
  description = "Path to the Helm chart directory (relative or absolute)"
  type        = string
  default     = "../helm-dir"
  nullable    = false
}

variable "helm_release_name" {
  description = "Name of the Helm release"
  type        = string
  default     = "mainwebsite"
  nullable    = false

  validation {
    condition     = can(regex("^[a-z0-9]([a-z0-9-]*[a-z0-9])?$", var.helm_release_name))
    error_message = "Helm release name must be a valid Kubernetes resource name."
  }
}

variable "helm_timeout" {
  description = "Timeout for Helm deployment in seconds"
  type        = number
  default     = 300
  nullable    = false

  validation {
    condition     = var.helm_timeout > 0 && var.helm_timeout <= 3600
    error_message = "Helm timeout must be between 1 and 3600 seconds."
  }
}

variable "helm_atomic_deployment" {
  description = "If true, helm upgrade process rolls back changes on failure"
  type        = bool
  default     = true
  nullable    = false
}

variable "helm_set_values" {
  description = "Additional Helm values to set via command line"
  type        = map(string)
  default     = {}
  nullable    = false
}

################################################################################
# Container Image Configuration
################################################################################

variable "mainwebsite_image_tag" {
  description = "Docker image tag for the mainwebsite service"
  type        = string
  default     = "latest"
  nullable    = false

  validation {
    condition     = length(var.mainwebsite_image_tag) > 0
    error_message = "Image tag must not be empty."
  }
}

variable "metrics_image_tag" {
  description = "Docker image tag for the metrics service"
  type        = string
  default     = "latest"
  nullable    = false

  validation {
    condition     = length(var.metrics_image_tag) > 0
    error_message = "Image tag must not be empty."
  }
}

################################################################################
# Optional: Remote State Configuration (uncomment to use)
################################################################################

# variable "state_bucket" {
#   description = "GCS bucket for storing Terraform state"
#   type        = string
#   default     = ""
#   nullable    = false
# }

# variable "state_encryption_key" {
#   description = "Encryption key for state file (base64 encoded 32-byte key)"
#   type        = string
#   sensitive   = true
#   default     = ""
# }

################################################################################
# Optional: Labels and Tags
################################################################################

variable "common_labels" {
  description = "Common labels to apply to all resources"
  type        = map(string)
  default = {
    managed_by = "terraform"
    project    = "aws-info-website"
  }
  nullable = false
}

################################################################################
# Terraform State Management (S3 Backend)
################################################################################

variable "terraform_state_bucket" {
  description = "S3 bucket name for storing Terraform state"
  type        = string
  nullable    = false

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9.-]*[a-z0-9]$", var.terraform_state_bucket))
    error_message = "Terraform state bucket must be a valid S3 bucket name."
  }
}

variable "terraform_state_key" {
  description = "S3 key path for Terraform state files"
  type        = string
  default     = "aws-info-website/terraform"
  nullable    = false

  validation {
    condition     = length(var.terraform_state_key) > 0
    error_message = "Terraform state key must not be empty."
  }
}

