# Terraform Helm Integration - Documentation Index

This index helps you navigate the Helm integration documentation and find what you need.

## 📋 Start Here

**New to this integration?** Start with one of these:

1. **[HELM_QUICK_REFERENCE.md](HELM_QUICK_REFERENCE.md)** ← **Start here!**
   - 5-minute quick start
   - Common operations with examples
   - Troubleshooting tips
   - File overview

2. **[IMPROVEMENTS_SUMMARY.md](IMPROVEMENTS_SUMMARY.md)** ← **Read this next**
   - What's new and why
   - Feature comparison
   - Migration guide
   - Summary of improvements

## 📚 Complete Documentation

### For Complete Understanding
- **[HELM_INTEGRATION_GUIDE.md](HELM_INTEGRATION_GUIDE.md)** (500+ lines)
  - Architecture overview
  - Configuration walkthrough
  - Detailed deployment steps
  - Advanced values management
  - Troubleshooting guide
  - Best practices
  - Related documentation links

## 🗂️ File Organization

### Terraform Configuration Files
```
terraform/
├── helm.tf                    # Helm provider & releases
├── helm-variables.tf          # Helm variables (30+)
├── helm-locals.tf             # Computed Helm values
├── helm-outputs.tf            # Helm status outputs
├── main.tf                    # EKS cluster (updated)
├── variables.tf               # General variables
├── locals.tf                  # General computed values
└── outputs.tf                 # Infrastructure outputs
```

### Documentation Files
```
terraform/
├── HELM_QUICK_REFERENCE.md         # 5-minute guide
├── HELM_INTEGRATION_GUIDE.md       # Complete guide
├── IMPROVEMENTS_SUMMARY.md         # What's new
├── HELM_INDEX.md                   # This file (Helm documentation index)
└── INDEX.md                        # General Terraform documentation index
```

### Utility Files
```
terraform/
├── environments/
│   ├── helm-example.tfvars    # Configuration template
│   ├── dev.tfvars             # Development config
│   ├── staging.tfvars         # Staging config
│   └── production.tfvars       # Production config
└── verify-helm-deployment.sh   # Verification script
```

### Helm Chart
```
helm-dir/
├── Chart.yaml                 # Chart metadata
├── values.yaml                # Default values
├── values-dev.yaml            # Dev overrides
├── values-staging.yaml        # Staging overrides
├── values-production.yaml     # Production overrides
├── templates/                 # Helm templates
└── README.md                  # Chart documentation
```

## 🎯 Find What You Need

### I want to...

**...deploy for the first time**
→ [HELM_QUICK_REFERENCE.md#quick-start](HELM_QUICK_REFERENCE.md)

**...understand the new architecture**
→ [HELM_INTEGRATION_GUIDE.md#architecture-overview](HELM_INTEGRATION_GUIDE.md)

**...update image tags**
→ [HELM_QUICK_REFERENCE.md#update-image-tags](HELM_QUICK_REFERENCE.md)

**...change replica counts**
→ [HELM_QUICK_REFERENCE.md#change-replica-count](HELM_QUICK_REFERENCE.md)

**...set up environment-specific config**
→ [HELM_INTEGRATION_GUIDE.md#values-management](HELM_INTEGRATION_GUIDE.md)

**...debug a failed deployment**
→ [HELM_QUICK_REFERENCE.md#troubleshooting](HELM_QUICK_REFERENCE.md)

**...understand values hierarchy**
→ [HELM_QUICK_REFERENCE.md#values-hierarchy](HELM_QUICK_REFERENCE.md)

**...see all available variables**
→ [helm-variables.tf](helm-variables.tf)

**...understand computed values**
→ [helm-locals.tf](helm-locals.tf)

**...see what outputs are available**
→ [helm-outputs.tf](helm-outputs.tf)

**...verify deployment is healthy**
→ [verify-helm-deployment.sh](verify-helm-deployment.sh)

**...learn Helm best practices**
→ [HELM_INTEGRATION_GUIDE.md#best-practices](HELM_INTEGRATION_GUIDE.md)

**...migrate from old configuration**
→ [IMPROVEMENTS_SUMMARY.md#migration-guide](IMPROVEMENTS_SUMMARY.md)

## 🚀 Quick Commands

```bash
# Deploy
terraform plan -var-file="environments/dev.tfvars"
terraform apply -var-file="environments/dev.tfvars"

# Check status
terraform output helm_commands
helm status mainwebsite -n production

# Verify health
bash verify-helm-deployment.sh

# Update image
terraform apply -var-file="environments/prod.tfvars" \
  -var="mainwebsite_image_tag=v1.2.3"

# Redeploy Helm only
terraform apply -target=helm_release.mainwebsite \
  -var-file="environments/prod.tfvars"

# Rollback
helm rollback mainwebsite 1 -n production
```

## 📖 Documentation by Topic

### Getting Started
- [Quick Start Guide](HELM_QUICK_REFERENCE.md#quick-start)
- [File Overview](HELM_QUICK_REFERENCE.md#file-overview)
- [Example Configuration](environments/helm-example.tfvars)

### Configuration
- [Configuration Guide](HELM_INTEGRATION_GUIDE.md#configuration)
- [Helm Variables](helm-variables.tf)
- [Environment Setup](environments/helm-example.tfvars)

### Deployment
- [Deployment Steps](HELM_INTEGRATION_GUIDE.md#deployment)
- [Common Tasks](HELM_INTEGRATION_GUIDE.md#common-tasks)
- [Verification Script](verify-helm-deployment.sh)

### Values Management
- [Values Hierarchy](HELM_QUICK_REFERENCE.md#values-hierarchy)
- [Values Configuration](HELM_INTEGRATION_GUIDE.md#values-management)
- [Computed Values](helm-locals.tf)
- [Helm Values Files](helm-dir/)

### Troubleshooting
- [Quick Troubleshooting](HELM_QUICK_REFERENCE.md#troubleshooting)
- [Detailed Troubleshooting](HELM_INTEGRATION_GUIDE.md#troubleshooting)
- [Verification Script](verify-helm-deployment.sh)

### Best Practices
- [Quick Best Practices](HELM_QUICK_REFERENCE.md#best-practices)
- [Detailed Best Practices](HELM_INTEGRATION_GUIDE.md#best-practices)
- [Terraform Helm Provider Docs](https://registry.terraform.io/providers/hashicorp/helm/latest/docs)

## 📊 Feature Reference

### New Files (9 total)
- ✅ helm.tf - Helm provider & releases
- ✅ helm-variables.tf - 30+ variables
- ✅ helm-locals.tf - Computed values
- ✅ helm-outputs.tf - Status outputs
- ✅ HELM_INTEGRATION_GUIDE.md - Complete guide
- ✅ HELM_QUICK_REFERENCE.md - Quick reference
- ✅ IMPROVEMENTS_SUMMARY.md - What's new
- ✅ HELM_INDEX.md - This file
- ✅ verify-helm-deployment.sh - Verification

### Key Improvements
- ✅ Modular architecture
- ✅ 30+ Helm variables
- ✅ Environment-specific config
- ✅ Values hierarchy and merging
- ✅ Computed values and timeouts
- ✅ 20+ useful outputs
- ✅ Service account support
- ✅ Comprehensive documentation
- ✅ Verification script
- ✅ Example configuration

## 🔗 External Resources

- [Terraform Helm Provider](https://registry.terraform.io/providers/hashicorp/helm/latest/docs)
- [Terraform Kubernetes Provider](https://registry.terraform.io/providers/hashicorp/kubernetes/latest/docs)
- [Helm Documentation](https://helm.sh/docs/)
- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)
- [AWS EKS Best Practices](https://aws.amazon.com/eks/best-practices/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

## 💡 Tips

1. **Always start with HELM_QUICK_REFERENCE.md** - It's short and covers most use cases
2. **Use environment-specific tfvars files** - Keep dev/staging/prod separate
3. **Run verify-helm-deployment.sh after deployment** - Instant health check
4. **Keep helm-dir/values.yaml clean** - Use environment-specific overrides
5. **Pin chart versions in production** - Use helm_chart_version for reproducibility

## ❓ Common Questions

**Q: How do I deploy to multiple environments?**
A: Create separate tfvars files (dev.tfvars, staging.tfvars, production.tfvars) with environment-specific values.
→ See [HELM_INTEGRATION_GUIDE.md](HELM_INTEGRATION_GUIDE.md)

**Q: How do I update image tags?**
A: Use `mainwebsite_image_tag` and `metrics_image_tag` variables or `helm_set_values` map.
→ See [HELM_QUICK_REFERENCE.md#Update-Image-Tags](HELM_QUICK_REFERENCE.md)

**Q: What if deployment fails?**
A: Run verify-helm-deployment.sh, check helm status, check pod logs.
→ See [HELM_QUICK_REFERENCE.md#Troubleshooting](HELM_QUICK_REFERENCE.md)

**Q: How do I rollback?**
A: Use `helm rollback mainwebsite 1 -n production`
→ See [HELM_QUICK_REFERENCE.md#Rollback-Release](HELM_QUICK_REFERENCE.md)

**Q: What variables are available?**
A: See helm-variables.tf for complete list with descriptions.
→ See [helm-variables.tf](helm-variables.tf)

## 📈 Next Steps

1. **Read** [HELM_QUICK_REFERENCE.md](HELM_QUICK_REFERENCE.md) - 5 minutes
2. **Read** [IMPROVEMENTS_SUMMARY.md](IMPROVEMENTS_SUMMARY.md) - 10 minutes
3. **Review** [environments/helm-example.tfvars](environments/helm-example.tfvars) - 5 minutes
4. **Copy and update** your tfvars file with actual config
5. **Run** `terraform plan` to see what will be created
6. **Run** `terraform apply` to deploy
7. **Run** `bash verify-helm-deployment.sh` to verify
8. **Read** [HELM_INTEGRATION_GUIDE.md](HELM_INTEGRATION_GUIDE.md) for deep dive

---

**Last Updated:** January 2026
**Documentation Version:** 1.0
**Terraform Version:** 1.0+
**Helm Version:** 3.0+
**AWS Provider Version:** Latest
