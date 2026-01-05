# Terraform Helm Integration Best Practices

This guide covers the improved Terraform Helm integration architecture and best practices for deploying Helm charts to your EKS cluster.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [File Structure](#file-structure)
3. [Configuration](#configuration)
4. [Deployment](#deployment)
5. [Values Management](#values-management)
6. [Common Tasks](#common-tasks)
7. [Troubleshooting](#troubleshooting)

## Architecture Overview

The improved Helm integration is organized into modular, maintainable Terraform files:

- **helm.tf** - Helm provider configuration and chart deployments
- **helm-variables.tf** - All Helm-specific variables with validation
- **helm-locals.tf** - Computed values and environment-specific configurations
- **helm-outputs.tf** - Outputs for Helm release status and useful commands

### Key Improvements

✅ **Separation of Concerns** - Helm configuration is isolated in dedicated files
✅ **Environment-Specific Values** - Automatic loading of environment-specific configurations
✅ **Comprehensive Outputs** - Useful commands and status information for debugging
✅ **Better Validation** - Input variables have proper validation rules
✅ **Computed Values** - Local values automatically adjust based on environment
✅ **Service Account Support** - Optional service account creation for RBAC
✅ **Enhanced Error Handling** - Atomic deployments with automatic rollback

## File Structure

```
terraform/
├── helm.tf                 # Helm provider and release definitions
├── helm-variables.tf       # Helm-specific variables
├── helm-locals.tf          # Computed Helm values
├── helm-outputs.tf         # Helm release outputs
├── main.tf                 # EKS cluster configuration
├── variables.tf            # General Terraform variables
├── locals.tf               # General computed values
├── outputs.tf              # General infrastructure outputs
├── terraform.tf            # Terraform version constraints
├── backend.tf              # Remote state configuration
└── environments/
    ├── dev.tfvars          # Development environment
    ├── staging.tfvars      # Staging environment
    └── production.tfvars   # Production environment

helm-dir/
├── Chart.yaml              # Helm chart metadata
├── values.yaml             # Default values
├── values-dev.yaml         # Dev-specific values
├── values-staging.yaml     # Staging-specific values
├── values-production.yaml  # Production-specific values
├── templates/              # Helm templates
└── README.md               # Chart documentation
```

## Configuration

### Basic Setup

1. **Initialize Terraform** with AWS backend:

```bash
cd terraform
terraform init
```

2. **Prepare environment variables**:

```bash
cp environments/example-dev.tfvars environments/dev.tfvars
```

3. **Configure your values** in `environments/dev.tfvars`:

```hcl
# Required AWS configuration
region           = "us-east-1"
cluster_name     = "my-eks-cluster"
subnet_ids       = ["subnet-xxxxx", "subnet-yyyyy"]

# Helm configuration
helm_release_name = "mainwebsite"
helm_chart_path   = "../helm-dir"
kubernetes_namespace = "production"

# Image tags
mainwebsite_image_tag = "v1.0.0"
metrics_image_tag     = "v1.0.0"
```

### Helm-Specific Variables

The new `helm-variables.tf` file provides extensive configuration options:

```hcl
# Chart configuration
helm_chart_path       = "../helm-dir"          # Local chart path
helm_chart_version    = "0.1.0"                # Chart version (optional)
helm_release_name     = "mainwebsite"          # Release name

# Deployment behavior
helm_timeout          = 300                    # Timeout in seconds
helm_atomic_deployment = true                  # Rollback on failure
helm_wait             = true                   # Wait for resources
helm_wait_for_jobs    = false                  # Wait for Kubernetes jobs
helm_max_history      = 10                     # Keep 10 revisions

# Values configuration
helm_set_values = {
  "mainwebsite.replicaCount" = "3"
  "metrics.enabled" = "true"
}

# Sensitive values (e.g., secrets, API keys)
helm_set_sensitive_values = {
  "recaptchaSecret" = var.recaptcha_secret
  "apiKey"          = var.api_key
}

# Environment-specific values files
helm_values_files = [
  "${path.module}/../helm-dir/values-${var.environment}.yaml"
]
```

## Deployment

### Plan the Deployment

```bash
terraform plan -var-file="environments/dev.tfvars"
```

Review the plan to see:
- EKS cluster creation (if `create_cluster = true`)
- Kubernetes namespace creation
- Helm release deployment

### Apply the Configuration

```bash
terraform apply -var-file="environments/dev.tfvars"
```

Terraform will:
1. Create/update the EKS cluster
2. Create the Kubernetes namespace
3. Deploy the Helm chart
4. Display useful outputs including Helm commands

### Dry Run (Preview Helm Chart)

To preview the rendered Kubernetes manifests without applying:

```bash
terraform plan -var-file="environments/dev.tfvars" -out=tfplan
helm template mainwebsite ../helm-dir -n production
```

## Values Management

### Value Hierarchy

Helm values are applied in this order (later values override earlier):

1. **Default values** - `helm-dir/values.yaml`
2. **Environment-specific values** - `helm-dir/values-{environment}.yaml`
3. **TFVars file values** - `helm_values_files` and `helm_set_values` in tfvars
4. **Sensitive values** - `helm_set_sensitive_values` (highest priority)

### Example: Environment-Specific Configuration

**helm-dir/values.yaml** (default):
```yaml
mainwebsite:
  replicaCount: 1
  image:
    repository: myregistry/mainwebsite
    tag: latest
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
```

**helm-dir/values-production.yaml** (production override):
```yaml
mainwebsite:
  replicaCount: 3
  image:
    tag: v1.2.3
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
```

**environments/production.tfvars**:
```hcl
helm_set_values = {
  "mainwebsite.image.tag" = "v1.2.3"
  "mainwebsite.replicaCount" = "3"
}
```

## Common Tasks

### 1. Update Helm Chart Version

```bash
# Update helm-variables.tf or tfvars
terraform apply -var-file="environments/prod.tfvars" \
  -var="helm_chart_version=0.2.0"
```

### 2. Modify Replica Count

Update `environments/dev.tfvars`:
```hcl
helm_set_values = {
  "mainwebsite.replicaCount" = "5"
}
```

Then apply:
```bash
terraform apply -var-file="environments/dev.tfvars"
```

### 3. Redeploy Without Infrastructure Changes

```bash
# Target only the Helm release
terraform apply -var-file="environments/dev.tfvars" \
  -target=helm_release.mainwebsite
```

### 4. Update Image Tags

```hcl
# In environments/dev.tfvars
mainwebsite_image_tag = "v2.0.0"
metrics_image_tag     = "v1.5.0"
```

### 5. Rollback to Previous Helm Release

```bash
# Get the release history
helm history mainwebsite -n production

# Rollback to revision 2
helm rollback mainwebsite 2 -n production
```

### 6. View Helm Release Status

Use the output commands provided by Terraform:

```bash
# Get the command from outputs
terraform output helm_commands

# Then run
helm status mainwebsite -n production
helm get values mainwebsite -n production
helm get manifest mainwebsite -n production
```

## Troubleshooting

### Issue: Helm Release Deployment Fails

**Check Helm release status:**
```bash
helm status mainwebsite -n production
helm get manifest mainwebsite -n production
```

**Check Kubernetes resources:**
```bash
kubectl get pods -n production -l app=mainwebsite
kubectl describe pod -n production <pod-name>
kubectl logs -n production <pod-name>
```

**Check Terraform state:**
```bash
terraform state show helm_release.mainwebsite
```

### Issue: "Resource already exists"

The Helm release might already exist in the cluster. Options:

1. **Import existing release into Terraform:**
```bash
terraform import helm_release.mainwebsite mainwebsite
```

2. **Delete and recreate:**
```bash
helm delete mainwebsite -n production
terraform apply -var-file="environments/prod.tfvars"
```

### Issue: Values Not Applied

1. **Verify values hierarchy** - Check which values file is taking precedence
2. **Check rendered manifest:**
```bash
helm get manifest mainwebsite -n production
```

3. **Force update:**
```bash
terraform apply -var-file="environments/prod.tfvars" \
  -var="helm_force_update=true"
```

### Issue: Timeout During Deployment

Increase timeout in tfvars:
```hcl
helm_timeout = 600  # Increase from default 300 seconds
```

### Issue: Namespace Does Not Exist

The Terraform configuration automatically creates the namespace. If it doesn't:

```bash
# Create it manually
kubectl create namespace production

# Re-apply Terraform
terraform apply -var-file="environments/prod.tfvars"
```

## Best Practices

### 1. Always Use Atomic Deployments

```hcl
helm_atomic_deployment = true  # Rollback on failure
```

### 2. Use Environment-Specific Values Files

Create separate values files for each environment:
- `values.yaml` - shared defaults
- `values-dev.yaml` - development overrides
- `values-staging.yaml` - staging overrides
- `values-production.yaml` - production overrides

### 3. Keep Sensitive Values in Terraform

Use `helm_set_sensitive_values` for secrets:
```hcl
helm_set_sensitive_values = {
  "recaptchaSecret" = var.recaptcha_secret
}
```

### 4. Version Your Helm Charts

Always pin `helm_chart_version` in production:
```hcl
helm_chart_version = "0.1.0"
```

### 5. Use wait = true

Ensures Terraform waits for resources to be ready:
```hcl
helm_wait = true
```

### 6. Version Control

Store tfvars in version control (except secrets):
```bash
# .gitignore
*.tfvars.secret
*.tfstate*
```

### 7. Use Helm Hooks for Database Migrations

In your Helm chart templates:
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  annotations:
    "helm.sh/hook": pre-upgrade,pre-install
    "helm.sh/hook-weight": "-5"
```

### 8. Monitor Helm Releases

```bash
# Check release status
helm list -n production

# Get deployment history
helm history mainwebsite -n production

# Check for failed pods
kubectl get pods -n production --field-selector=status.phase=Failed
```

## Related Documentation

- [Terraform Helm Provider Documentation](https://registry.terraform.io/providers/hashicorp/helm/latest/docs)
- [Kubernetes Provider Documentation](https://registry.terraform.io/providers/hashicorp/kubernetes/latest/docs)
- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)
- [AWS EKS Best Practices](https://aws.amazon.com/eks/best-practices/)
