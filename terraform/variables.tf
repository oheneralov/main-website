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

variable "create_cluster" {
  description = "Whether to create a new EKS cluster (true) or reference an existing one (false)"
  type        = bool
  default     = true
  nullable    = false
}

variable "cluster_name" {
  description = "Name of the EKS cluster to create or reference"
  type        = string
  nullable    = false

  validation {
    condition     = length(var.cluster_name) > 0 && length(var.cluster_name) <= 100
    error_message = "Cluster name must be between 1 and 100 characters."
  }
}

variable "kubernetes_version" {
  description = "Kubernetes version to use for the EKS cluster"
  type        = string
  default     = "1.28"
  nullable    = false

  validation {
    condition     = can(regex("^1\\.[0-9]{2}$", var.kubernetes_version))
    error_message = "Kubernetes version must be in format 1.XX (e.g., 1.28)"
  }
}

variable "subnet_ids" {
  description = "List of subnet IDs for the EKS cluster and nodes"
  type        = list(string)
  nullable    = false

  validation {
    condition     = length(var.subnet_ids) >= 2
    error_message = "At least 2 subnets are required for EKS cluster"
  }
}

variable "cluster_security_group_ids" {
  description = "List of security group IDs to attach to the EKS cluster"
  type        = list(string)
  default     = []
  nullable    = false
}

variable "cluster_endpoint_public_access" {
  description = "Enable public access to the EKS cluster endpoint"
  type        = bool
  default     = true
  nullable    = false
}

variable "cluster_endpoint_public_access_cidrs" {
  description = "List of CIDR blocks that can access the public EKS endpoint"
  type        = list(string)
  default     = ["0.0.0.0/0"]
  nullable    = false
}

variable "cluster_log_types" {
  description = "List of control plane logging types to enable"
  type        = list(string)
  default     = ["api", "audit", "authenticator", "controllerManager", "scheduler"]
  nullable    = false

  validation {
    condition = alltrue([
      for log_type in var.cluster_log_types : contains(["api", "audit", "authenticator", "controllerManager", "scheduler"], log_type)
    ])
    error_message = "Valid log types are: api, audit, authenticator, controllerManager, scheduler"
  }
}

variable "node_group_min_size" {
  description = "Minimum number of nodes in the node group"
  type        = number
  default     = 2
  nullable    = false

  validation {
    condition     = var.node_group_min_size > 0 && var.node_group_min_size <= 100
    error_message = "Node group size must be between 1 and 100"
  }
}

variable "node_group_max_size" {
  description = "Maximum number of nodes in the node group"
  type        = number
  default     = 10
  nullable    = false

  validation {
    condition     = var.node_group_max_size > 0 && var.node_group_max_size <= 100
    error_message = "Node group size must be between 1 and 100"
  }
}

variable "node_group_desired_size" {
  description = "Desired number of nodes in the node group"
  type        = number
  default     = 3
  nullable    = false

  validation {
    condition     = var.node_group_desired_size > 0 && var.node_group_desired_size <= 100
    error_message = "Node group size must be between 1 and 100"
  }
}

variable "node_instance_types" {
  description = "List of EC2 instance types for the node group"
  type        = list(string)
  default     = ["t3.medium"]
  nullable    = false

  validation {
    condition = alltrue([
      for instance in var.node_instance_types : can(regex("^[a-z0-9]+\\.[a-z0-9]+$", instance))
    ])
    error_message = "Instance types must be valid AWS instance types (e.g., t3.medium)"
  }
}

variable "node_disk_size" {
  description = "Disk size in GB for each node"
  type        = number
  default     = 50
  nullable    = false

  validation {
    condition     = var.node_disk_size >= 20 && var.node_disk_size <= 16384
    error_message = "Disk size must be between 20 and 16384 GB"
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

