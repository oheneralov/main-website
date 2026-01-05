# Terraform Helm Integration - Quick Reference

## Quick Start

### 1. Prepare Configuration
```bash
cd terraform
cp environments/helm-example.tfvars environments/dev.tfvars
# Edit dev.tfvars with your actual AWS settings
```

### 2. Initialize Terraform
```bash
terraform init
```

### 3. Deploy
```bash
terraform plan -var-file="environments/dev.tfvars"
terraform apply -var-file="environments/dev.tfvars"
```

### 4. Get Status
```bash
terraform output helm_commands
# Then run any command from the output
```

---

## File Overview

| File | Purpose |
|------|---------|
| **helm.tf** | Helm provider, releases, namespaces |
| **helm-variables.tf** | All Helm-specific variables |
| **helm-locals.tf** | Computed values, environment config |
| **helm-outputs.tf** | Status and command outputs |
| **main.tf** | EKS cluster (updated) |
| **variables.tf** | General variables |
| **locals.tf** | General computed values |

---

## Key Features

✅ **Modular** - Helm config separated into dedicated files  
✅ **Flexible** - Support for local charts, remote repos, and values merging  
✅ **Safe** - Atomic deployments with automatic rollback on failure  
✅ **Observable** - Comprehensive outputs with useful commands  
✅ **Scalable** - Environment-specific configurations (dev/staging/prod)  
✅ **Documented** - Inline comments and comprehensive guides  

---

## Common Operations

### Update Image Tags
```hcl
# In environments/dev.tfvars
mainwebsite_image_tag = "v1.2.3"
metrics_image_tag     = "v1.2.3"

# Apply
terraform apply -var-file="environments/dev.tfvars"
```

### Change Replica Count
```hcl
# In environments/dev.tfvars
helm_set_values = {
  "mainwebsite.replicaCount" = "5"
}

terraform apply -var-file="environments/dev.tfvars"
```

### Redeploy Helm Only
```bash
terraform apply \
  -target=helm_release.mainwebsite \
  -var-file="environments/dev.tfvars"
```

### Check Release Status
```bash
# Get commands from Terraform
terraform output helm_commands

# Check status
helm status mainwebsite -n production
helm get values mainwebsite -n production
helm history mainwebsite -n production
```

### Rollback Release
```bash
# See revisions
helm history mainwebsite -n production

# Rollback to revision 1
helm rollback mainwebsite 1 -n production
```

---

## Values Hierarchy (Priority Order)

Lower → Higher (Higher overrides)

1. **Base values** - `helm-dir/values.yaml`
2. **Environment values** - `helm-dir/values-{env}.yaml` (auto-loaded)
3. **TFVars files** - `helm_values_files` variable
4. **Set values** - `helm_set_values` map
5. **Sensitive values** - `helm_set_sensitive_values` (highest)

**Example:**
```yaml
# values.yaml (default)
replicaCount: 1

# values-production.yaml
replicaCount: 3

# Terraform tfvars
helm_set_values = { "mainwebsite.replicaCount" = "5" }

# Result: 5 replicas (tfvars wins)
```

---

## Helm Deployment Options

```hcl
# Timeout for deployment (seconds)
helm_timeout = 300

# Rollback automatically if deployment fails
helm_atomic_deployment = true

# Wait for all resources to be ready
helm_wait = true

# Wait for Kubernetes jobs to complete
helm_wait_for_jobs = false

# Keep this many release revisions for rollback
helm_max_history = 10

# Cleanup on failure
helm_cleanup_on_fail = true

# Enable debug logging
helm_debug = false
```

---

## Environment-Specific Configuration

Create values files for each environment:

```
helm-dir/
├── values.yaml              # Shared defaults
├── values-dev.yaml          # Dev overrides
├── values-staging.yaml      # Staging overrides
└── values-production.yaml   # Production overrides
```

**Environment-specific tfvars:**
```
environments/
├── dev.tfvars
├── staging.tfvars
└── production.tfvars
```

---

## Troubleshooting

### Check Release Status
```bash
terraform output helm_commands
helm status mainwebsite -n production
```

### View Rendered Manifests
```bash
terraform output helm_manifest
# or
helm get manifest mainwebsite -n production
```

### Debug Pod Issues
```bash
kubectl get pods -n production -l app=mainwebsite
kubectl describe pod -n production <pod-name>
kubectl logs -n production <pod-name>
```

### View Recent Events
```bash
kubectl get events -n production --sort-by='.lastTimestamp'
```

### Import Existing Release
```bash
terraform import helm_release.mainwebsite mainwebsite
```

---

## Best Practices

1. **Always use `helm_atomic_deployment = true`** for safe deployments
2. **Keep `helm_wait = true`** to ensure resources are ready
3. **Use environment-specific values files** for different configs
4. **Version your charts** with `helm_chart_version`
5. **Store secrets separately** using `helm_set_sensitive_values`
6. **Test in dev** before applying to production
7. **Keep release history** for easy rollbacks (`helm_max_history`)
8. **Monitor logs** after deployments

---

## Documentation

- [Full Guide](HELM_INTEGRATION_GUIDE.md) - Complete Helm integration guide
- [Terraform Helm Provider](https://registry.terraform.io/providers/hashicorp/helm/latest/docs)
- [Kubernetes Provider](https://registry.terraform.io/providers/hashicorp/kubernetes/latest/docs)
- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)
- [EKS Best Practices](https://aws.amazon.com/eks/best-practices/)

---

## Variables Reference

### Chart Configuration
- `helm_chart_path` - Path to Helm chart directory
- `helm_chart_version` - Helm chart version
- `helm_release_name` - Name of Helm release

### Behavior
- `helm_timeout` - Deployment timeout in seconds
- `helm_atomic_deployment` - Rollback on failure
- `helm_wait` - Wait for resources to be ready
- `helm_wait_for_jobs` - Wait for Kubernetes jobs
- `helm_max_history` - Release revisions to keep
- `helm_cleanup_on_fail` - Cleanup on failure
- `helm_debug` - Enable debug logging

### Values
- `helm_set_values` - Individual values to set
- `helm_set_sensitive_values` - Sensitive values (secrets)
- `helm_values_files` - Additional values files
- `helm_inline_values` - Inline YAML values

---

## Useful Outputs

```bash
# Print all Helm-related outputs
terraform output

# Get specific output
terraform output helm_commands
terraform output helm_deployment_summary
terraform output verification_commands
```

---

## Next Steps

1. Read the [Full Guide](HELM_INTEGRATION_GUIDE.md)
2. Update your tfvars with actual AWS configuration
3. Run `terraform plan` to review changes
4. Run `terraform apply` to deploy
5. Use `terraform output helm_commands` to monitor
