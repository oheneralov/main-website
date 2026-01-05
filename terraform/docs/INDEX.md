# Terraform Documentation Index

Complete navigation guide for the Terraform infrastructure-as-code project.

---

## Quick Navigation

| Document | Purpose | Time | Audience |
|----------|---------|------|----------|
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | **Complete guide** (merged: overview, setup, commands, troubleshooting) | 30 min | Everyone |
| [BEST_PRACTICES.md](BEST_PRACTICES.md) | 20 best practices explained | 20 min | Developers |
| [CI_CD.md](CI_CD.md) | CI/CD integration pipelines | 15 min | DevOps/CI-CD |

**Note:** README.md, SETUP.md, QUICK_REFERENCE.md, and TROUBLESHOOTING.md have been consolidated into [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md). All content is preserved with duplicates removed.

---

## For Different Roles

### 👤 New Team Member

**Getting Started (30 minutes)**
1. Read [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Overview & quick start
2. Follow the **Installation & Setup** section
3. Run first deployment to dev environment
4. Check outputs: `terraform output`

**Key Commands**:
```bash
terraform plan -var-file="environments/dev.tfvars"
terraform apply -var-file="environments/dev.tfvars"
```

**Learn More**:
- [BEST_PRACTICES.md](BEST_PRACTICES.md) - Understand the architecture
- Variable meanings in [terraform/variables.tf](variables.tf)

---

### 👨‍💻 Terraform Developer

**Daily Work**
1. Review [BEST_PRACTICES.md](BEST_PRACTICES.md) first time
2. Reference [variables.tf](variables.tf) for configuration options
3. Check [locals.tf](locals.tf) for computed values
4. Review modules in [modules/gke-deployment/](modules/gke-deployment/)

**Common Tasks**:
- **Create new variable**: Edit [variables.tf](variables.tf)
- **Add new output**: Edit [outputs.tf](outputs.tf)
- **Override defaults**: Update [environments/*.tfvars](environments/)
- **Debug deployment**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

**Design Files to Understand**:
- [terraform.tf](terraform.tf) - Provider configuration
- [locals.tf](locals.tf) - Local values (DRY principle)
- [modules/](modules/) - Reusable code

---

### 🚀 DevOps Engineer

**Deployment**
1. Review [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Installation & setup
2. Plan changes: `terraform plan -var-file="environments/prod.tfvars"`
3. Review outputs carefully
4. Get approval from team
5. Apply: `terraform apply -var-file="environments/prod.tfvars"`

**Monitoring & Troubleshooting**
- Check [DEPLOYMENT_GUIDE.md - Troubleshooting](DEPLOYMENT_GUIDE.md#troubleshooting) section
- Check deployment: `kubectl get pods -n production`
- View logs: `kubectl logs -n production <pod-name>`
- Helm status: `helm status mainwebsite -n production`

**Production Safety**
- Never use "latest" image tags
- Always plan before apply
- Use version tags (e.g., v1.0.0)
- Backup state regularly
- Test in staging first

---

### 🔧 Platform/Infrastructure Lead

**Architecture & Planning**
1. Review entire [BEST_PRACTICES.md](BEST_PRACTICES.md)
2. Understand module structure in [modules/gke-deployment/](modules/gke-deployment/)
3. Review environment configs in [environments/](environments/)

**CI/CD Integration**
- See [CI_CD.md](CI_CD.md) for pipeline setup
- Configure GitHub Actions/Cloud Build
- Set up automated deployments

**Optimization & Scaling**
- Adjust replicas in Helm values
- Configure autoscaling in HPA
- Manage node pools in GKE

---

## File Structure Overview

```
terraform/
├── README.md                          # Project overview
├── SETUP.md                           # Getting started guide
├── BEST_PRACTICES.md                  # 20 best practices
├── TROUBLESHOOTING.md                 # Common issues
├── CI_CD.md                           # CI/CD pipelines
├── terraform.tf                       # Provider config (70 lines)
├── variables.tf                       # Input variables (170+ lines)
├── outputs.tf                         # Output values (100+ lines)
├── locals.tf                          # Computed values (40 lines)
├── main.tf                            # (Legacy - replace with modular approach)
├── modules/
│   └── gke-deployment/                # Reusable Kubernetes/Helm module
│       ├── main.tf                    # Module resources (55 lines)
│       ├── variables.tf               # Module inputs (65 lines)
│       └── outputs.tf                 # Module outputs (20 lines)
├── environments/
│   ├── dev.tfvars                     # Development config (25 lines)
│   ├── staging.tfvars                 # Staging config (28 lines)
│   ├── production.tfvars              # Production config (35 lines)
│   └── example-dev.tfvars             # Template for new envs (commented)
└── .gitignore                         # Security - excludes sensitive files
```

---

## Common Workflows

### 🟢 Deploy to Development

```bash
# 1. Plan changes
terraform plan -var-file="environments/dev.tfvars" -out=tfplan

# 2. Review plan
terraform show tfplan

# 3. Apply (immediate in dev)
terraform apply tfplan

# 4. Verify
terraform output
```

**Time**: ~5 minutes

---

### 🟡 Deploy to Staging (with Review)

```bash
# 1. Create feature branch
git checkout -b feature/update-staging

# 2. Update staging config
nano environments/staging.tfvars

# 3. Plan and commit
terraform plan -var-file="environments/staging.tfvars" > plan.txt
git add environments/staging.tfvars
git commit -m "Update staging configuration"

# 4. Create pull request
git push origin feature/update-staging
# Create PR on GitHub/GitLab

# 5. After approval, merge to main
# CI/CD will apply changes automatically
```

**Time**: ~15 minutes

---

### 🔴 Deploy to Production (with Caution)

```bash
# 1. Test in staging first
terraform apply -var-file="environments/staging.tfvars"

# 2. Plan production changes
terraform plan -var-file="environments/production.tfvars" -out=tfplan-prod

# 3. Show detailed plan
terraform show tfplan-prod | less

# 4. Get team approval
echo "Review complete. Ready for production?"

# 5. Apply production
terraform apply tfplan-prod

# 6. Verify thoroughly
kubectl get all -n production
helm status mainwebsite -n production
```

**Time**: ~20 minutes

---

### 🔧 Debug Deployment Issues

```bash
# See TROUBLESHOOTING.md for detailed steps

# 1. Check Terraform state
terraform state list
terraform show

# 2. Check Kubernetes resources
kubectl get pods -n production
kubectl describe pod <pod-name> -n production

# 3. Check Helm release
helm status mainwebsite -n production
helm get values mainwebsite -n production

# 4. Check application logs
kubectl logs <pod-name> -n production

# 5. Reference TROUBLESHOOTING.md
# Search for your error message
```

---

### 📊 View Infrastructure

```bash
# See all outputs
terraform output

# Get specific output
terraform output -raw gke_cluster_endpoint
terraform output -json | jq '.mainwebsite_namespace'

# List all resources
terraform state list

# Show resource details
terraform state show 'kubernetes_namespace.default'

# Export state to JSON
terraform show -json | jq > state.json
```

---

## Configuration Quick Reference

### Environment Selection

```bash
# Development (single node, dev images)
terraform apply -var-file="environments/dev.tfvars"

# Staging (2 nodes, staging images, autoscaling)
terraform apply -var-file="environments/staging.tfvars"

# Production (3 nodes, version tags, aggressive autoscaling)
terraform apply -var-file="environments/production.tfvars"
```

### Key Variables Explained

| Variable | Purpose | Dev | Staging | Prod |
|----------|---------|-----|---------|------|
| `mainwebsite_image_tag` | App version | dev-latest | staging-latest | v1.0.0 |
| `cluster_initial_node_count` | Cluster size | 1 | 2 | 3 |
| `helm_timeout` | Deploy timeout | 300s | 300s | 600s |
| `helm_atomic_deployment` | Rollback on fail | true | true | true |

---

## Important Files Explained

### [terraform.tf](terraform.tf)
- **Purpose**: Terraform version constraints and provider configuration
- **Key Points**:
  - Terraform >= 1.0
  - Google, Kubernetes, Helm providers
  - Default labels for all GCP resources
  - Data source for GKE cluster

### [variables.tf](variables.tf)
- **Purpose**: Define all input variables with validation
- **Contains**:
  - 170+ lines of variable definitions
  - Type specifications
  - Descriptions and defaults
  - Validation rules (regex, enum)
  - Sensitive data marking

### [outputs.tf](outputs.tf)
- **Purpose**: Return useful information after apply
- **Includes**:
  - GKE cluster details
  - Kubernetes endpoint
  - Helm release status
  - Helpful kubectl/helm commands

### [locals.tf](locals.tf)
- **Purpose**: Define computed values (DRY principle)
- **Contains**:
  - Resource naming conventions
  - Environment-specific configs
  - Common labels
  - Dynamic values

### [modules/gke-deployment/main.tf](modules/gke-deployment/main.tf)
- **Purpose**: Reusable module for Kubernetes namespace + Helm release
- **Handles**:
  - Namespace creation
  - Helm chart deployment
  - Resource management

---

## Key Concepts

### Environments
- **Dev**: Fast iteration, single node, latest images
- **Staging**: Production-like, multiple nodes, autoscaling
- **Prod**: High availability, version tags, monitoring

### Tfvars Files
- Contains environment-specific values
- Overrides defaults in variables.tf
- Never committed to version control (mostly)
- One per environment

### Helm Integration
- Manages Kubernetes resources
- Configured via helm_set_values map
- Supports atomic deployments
- Integrates with Prometheus monitoring

### State Management
- Local state by default (can enable GCS backend)
- Tracks all infrastructure
- Should be backed up regularly
- Sensitive data marked accordingly

---

## External Resources

### Official Documentation
- [Terraform Documentation](https://www.terraform.io/docs)
- [GCP Provider Docs](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Kubernetes Provider Docs](https://registry.terraform.io/providers/hashicorp/kubernetes/latest/docs)
- [Helm Provider Docs](https://registry.terraform.io/providers/hashicorp/helm/latest/docs)

### GCP Resources
- [GKE Documentation](https://cloud.google.com/kubernetes-engine/docs)
- [GCP Terraform Best Practices](https://cloud.google.com/docs/terraform/best-practices-for-terraform)
- [Service Accounts Guide](https://cloud.google.com/iam/docs/service-accounts)

### Kubernetes Resources
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)

---

## Frequently Asked Questions

### Q: How do I add a new environment?

**A**: Follow these steps:
1. Copy `environments/dev.tfvars` to `environments/new-env.tfvars`
2. Update values for your environment
3. Run: `terraform apply -var-file="environments/new-env.tfvars"`

See [SETUP.md](SETUP.md) for detailed instructions.

### Q: How do I deploy a new application version?

**A**: Update the image tag:
1. Edit `environments/prod.tfvars`
2. Change `mainwebsite_image_tag = "v1.0.1"`
3. Run: `terraform plan -var-file="environments/prod.tfvars"`
4. Review and apply

### Q: How do I scale the cluster?

**A**: Adjust replicas:
1. Edit `environments/prod.tfvars`
2. Update: `"mainwebsite.replicaCount" = "5"`
3. Apply changes

### Q: How do I rollback a deployment?

**A**: Multiple options:
1. Revert image tag in tfvars
2. Use Helm: `helm rollback mainwebsite -n production`
3. Restore previous Terraform state

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for emergency procedures.

### Q: How do I backup my state?

**A**: Multiple approaches:
1. Enable GCS backend (recommended)
2. Regular file backups: `cp terraform.tfstate backup.tfstate`
3. Git commits track history

### Q: What's the difference between tfvars files?

**A**: Different configurations per environment:
- **dev.tfvars**: Single node, dev images, minimal resources
- **staging.tfvars**: 2 nodes, staging images, autoscaling
- **production.tfvars**: 3 nodes, version tags, max autoscaling

---

## Support & Troubleshooting

### Something doesn't work?

1. **Check [DEPLOYMENT_GUIDE.md - Troubleshooting](DEPLOYMENT_GUIDE.md#troubleshooting)** - Most issues covered
2. **Review plan carefully** - `terraform show tfplan`
3. **Check state** - `terraform state list`
4. **View logs** - `kubectl logs -n production <pod-name>`
5. **Check events** - `kubectl get events -n production`

### Need help?

- Team members familiar with Terraform
- Review [BEST_PRACTICES.md](BEST_PRACTICES.md) for patterns
- Check provider documentation links in [DEPLOYMENT_GUIDE.md - Additional Resources](DEPLOYMENT_GUIDE.md#additional-resources)
- Reference [CI_CD.md](CI_CD.md) for automation issues

---

## Document Versions

| Document | Version | Last Updated | Maintainer |
|----------|---------|--------------|-----------|
| README.md | 1.0 | 2026-01-02 | Platform Team |
| SETUP.md | 1.0 | 2026-01-02 | Platform Team |
| BEST_PRACTICES.md | 1.0 | 2026-01-02 | Platform Team |
| TROUBLESHOOTING.md | 1.0 | 2026-01-02 | DevOps Team |
| CI_CD.md | 1.0 | 2026-01-02 | DevOps Team |

---

## Checklist: You're Ready If...

- [ ] You can navigate between documents
- [ ] You understand the file structure
- [ ] You know which document to read for your role
- [ ] You've completed the [SETUP.md](SETUP.md) first steps
- [ ] You can run: `terraform plan -var-file="environments/dev.tfvars"`
- [ ] You understand the difference between environments
- [ ] You know where to find help (this index + [TROUBLESHOOTING.md](TROUBLESHOOTING.md))

---

**Last Updated**: January 2, 2026  
**Maintained by**: Infrastructure Team  
**Questions?**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or contact platform-team@company.com
