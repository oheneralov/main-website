################################################################################
# Helm-Specific Variables
################################################################################
# Extended Helm configuration variables for better control and flexibility

################################################################################
# Helm Chart Configuration
################################################################################

variable "helm_chart_path" {
  description = "Path to the Helm chart directory (relative or absolute)"
  type        = string
  default     = "../helm-dir"
  nullable    = false

  validation {
    condition     = length(var.helm_chart_path) > 0
    error_message = "Helm chart path must not be empty."
  }
}

variable "helm_chart_version" {
  description = "Version of the Helm chart to deploy"
  type        = string
  default     = ""
  nullable    = false

  # Empty string means use the version in Chart.yaml
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

################################################################################
# Helm Deployment Behavior
################################################################################

variable "helm_timeout" {
  description = "Timeout for Helm deployment in seconds"
  type        = number
  default     = 900
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

variable "helm_wait" {
  description = "If true, Terraform will wait for resources to be ready"
  type        = bool
  default     = true
  nullable    = false
}

variable "helm_wait_for_jobs" {
  description = "If true, Terraform will wait for jobs to complete"
  type        = bool
  default     = false
  nullable    = false
}

variable "helm_recreate_pods" {
  description = "Recreate pods when their configuration changes"
  type        = bool
  default     = false
  nullable    = false
}

variable "helm_force_update" {
  description = "Force resource update even if nothing changed"
  type        = bool
  default     = false
  nullable    = false
}

variable "helm_cleanup_on_fail" {
  description = "Cleanup resources on failure"
  type        = bool
  default     = true
  nullable    = false
}

variable "helm_debug" {
  description = "Enable Helm debug logging"
  type        = bool
  default     = false
  nullable    = false
}

variable "helm_max_history" {
  description = "Max number of release revisions stored in history"
  type        = number
  default     = 10
  nullable    = false

  validation {
    condition     = var.helm_max_history > 0 && var.helm_max_history <= 100
    error_message = "Helm max history must be between 1 and 100."
  }
}

################################################################################
# Helm Values Configuration
################################################################################

variable "helm_values_files" {
  description = "List of values YAML files to merge (in order of precedence)"
  type        = list(string)
  default     = []
  nullable    = false
}

variable "helm_inline_values" {
  description = "List of inline Helm values (YAML format as strings)"
  type        = list(string)
  default     = []
  nullable    = false
}

variable "helm_set_values" {
  description = "Individual Helm values to set via --set (key=value map)"
  type        = map(string)
  default     = {}
  nullable    = false
}

variable "helm_set_sensitive_values" {
  description = "Sensitive Helm values to set via --set (e.g., passwords, tokens)"
  type        = map(string)
  default     = {}
  nullable    = false
  sensitive   = true
}

################################################################################
# Helm Repository Configuration (for future use)
################################################################################

variable "helm_repository_url" {
  description = "Helm repository URL (for pulling charts from remote repositories)"
  type        = string
  default     = ""
  nullable    = false

  # Empty string means use local chart
}

variable "helm_repository_username" {
  description = "Username for private Helm repository"
  type        = string
  default     = ""
  nullable    = false
  sensitive   = true
}

variable "helm_repository_password" {
  description = "Password for private Helm repository"
  type        = string
  default     = ""
  nullable    = false
  sensitive   = true
}

################################################################################
# Helm Service Account
################################################################################

variable "create_helm_service_account" {
  description = "Whether to create a service account for Helm operations"
  type        = bool
  default     = false
  nullable    = false
}

################################################################################
# Helm Chart Repository (for remote charts)
################################################################################

variable "helm_chart_repository" {
  description = "Helm chart repository name (e.g., stable, bitnami)"
  type        = string
  default     = ""
  nullable    = false

  # Empty string means use local chart path
}

variable "helm_chart_namespace" {
  description = "Namespace where Helm chart is located in the repository"
  type        = string
  default     = ""
  nullable    = false
}
################################################################################
# CRD Installation Variables
################################################################################

variable "install_traefik_crds" {
  description = "Whether to install Traefik CRDs (required for IngressRoute)"
  type        = bool
  default     = true
  nullable    = false
}

variable "traefik_crd_version" {
  description = "Version of Traefik Helm chart for CRD installation"
  type        = string
  default     = "30.0.0" # Adjust based on your needs
  nullable    = false
}

variable "install_prometheus_crds" {
  description = "Whether to install Prometheus Operator CRDs (ServiceMonitor, PodMonitor, etc.)"
  type        = bool
  default     = true
  nullable    = false
}

variable "prometheus_crd_chart_version" {
  description = "Version of the prometheus-operator-crds chart to install (null = latest)"
  type        = string
  default     = null
}
################################################################################
# Kubernetes Deployment Control
################################################################################

variable "deploy_kubernetes_manifests" {
  description = "Whether to deploy Kubernetes manifests via Helm during terraform apply. Set to false to skip K8s deployment and use the deploy-docker-and-k8s.sh script instead."
  type        = bool
  default     = true
  nullable    = false
}