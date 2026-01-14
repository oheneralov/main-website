# Quick Reference: Docker Build, Push & K8s Deployment

## One-Line Commands

### Full Deployment (Build Docker + Deploy K8s)
```bash
# Linux/macOS
./terraform/deploy-docker-and-k8s.sh -e dev -c 123456789012

# Windows PowerShell
.\terraform\deploy-docker-and-k8s.ps1 -Environment dev -RegistryId 123456789012
```

### Only Deploy K8s (Skip Docker Build)
```bash
# Linux/macOS
./terraform/deploy-docker-and-k8s.sh -e dev --skip-docker

# Windows PowerShell
.\terraform\deploy-docker-and-k8s.ps1 -Environment dev -SkipDocker
```

### Only Build & Push Docker (Skip K8s)
```bash
# Linux/macOS
./terraform/deploy-docker-and-k8s.sh -e dev -c 123456789012 --skip-k8s

# Windows PowerShell
.\terraform\deploy-docker-and-k8s.ps1 -Environment dev -RegistryId 123456789012 -SkipK8s
```

---

## Terraform Setup

### 1. Configure Environment File

Edit `terraform/environments/dev.tfvars`:
```hcl
# Set to false to skip K8s deployment during terraform apply
deploy_kubernetes_manifests = false
```

### 2. Apply Infrastructure
```bash
cd terraform
terraform apply -var-file="environments/dev.tfvars"
```

---

## Deployment Script Options

### Required Parameters
- `-e, --environment` - Environment: `dev` (only supported environment)
- `-c, --registry-id` - AWS Account ID (required unless `--skip-docker`)

### Optional Parameters
- `-r, --region` - AWS region (default: `us-east-1`)
- `-n, --namespace` - K8s namespace (default: `development`)
- `-h, --helm-chart-path` - Helm chart path (default: `../helm-dir`)
- `-s, --skip-docker` - Skip Docker build and push
- `-k, --skip-k8s` - Skip Kubernetes deployment

---

## Common Workflows

### Development Deployment
```bash
# 1. Setup infrastructure once
terraform init
terraform apply -var-file="environments/dev.tfvars"

# 2. Deploy/update applications (repeat as needed)
./deploy-docker-and-k8s.sh -e dev -c 123456789012

# 3. Re-deploy only K8s (e.g., after config changes)
./deploy-docker-and-k8s.sh -e dev -s
```

### Quick Image Rebuild & Deploy
```bash
# Rebuild images and redeploy without full setup
./deploy-docker-and-k8s.sh -e dev -c 123456789012 -r us-east-1
```

---

## Verify Deployment

### Check Pod Status
```bash
kubectl get pods -n development
```

### View Pod Logs
```bash
kubectl logs -f deployment/mainwebsite -n development
```

### Check Service
```bash
kubectl get svc -n development
```

### Helm Release Status
```bash
helm status mainwebsite -n development
```

### Describe Deployment
```bash
kubectl describe deployment mainwebsite -n development
```

---

## Troubleshooting Quick Fixes

### ECR Login Fails
```bash
# Verify AWS credentials
aws sts get-caller-identity

# Check ECR repository exists
aws ecr describe-repositories --region us-east-1
```

### Docker Build Fails
```bash
# Verify Docker is running
docker ps

# Manual build to test
docker build -f mainwebsite/Dockerfile -t mainwebsite:latest mainwebsite
```

### kubectl Access Issues
```bash
# Update kubeconfig
aws eks update-kubeconfig --region us-east-1 --name <cluster-name>

# Verify access
kubectl get nodes
```

### Helm Deployment Fails
```bash
# Check Helm chart
ls -la ../helm-dir/

# Validate chart
helm lint ../helm-dir/

# Check previous releases
helm history mainwebsite -n development

# Rollback if needed
helm rollback mainwebsite -n development
```

---

## Rollback

### Rollback Application
```bash
# View history
helm history mainwebsite -n development

# Rollback to previous version
helm rollback mainwebsite -n development

# Rollback to specific revision
helm rollback mainwebsite 3 -n development
```

### Rollback Infrastructure
```bash
# View terraform state
terraform show

# Destroy resources
terraform destroy -var-file="environments/dev.tfvars"
```

---

## Environment Variables

Set for convenience:
```bash
export AWS_REGION="us-east-1"
export AWS_ACCOUNT_ID="123456789012"
export K8S_NAMESPACE="development"

# Then use in scripts
./deploy-docker-and-k8s.sh -e dev -c $AWS_ACCOUNT_ID -r $AWS_REGION -n $K8S_NAMESPACE
```

---

## PowerShell Setup (Windows)

### Make Scripts Executable
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Run PowerShell Script
```powershell
.\terraform\deploy-docker-and-k8s.ps1 -Environment dev -RegistryId 123456789012
```

---

## Files Changed

| File | Purpose |
|------|---------|
| `terraform/helm-variables.tf` | New `deploy_kubernetes_manifests` variable |
| `terraform/helm.tf` | Updated Helm resources (conditional deployment) |
| `terraform/deploy-docker-and-k8s.sh` | Bash deployment script |
| `terraform/deploy-docker-and-k8s.ps1` | PowerShell deployment script |
| `terraform/DEPLOYMENT_GUIDE.md` | Comprehensive guide |
| `DEPLOYMENT_ARCHITECTURE_CHANGES.md` | Architecture documentation |

---

## Next Steps

1. ✓ Update `.tfvars` files: `deploy_kubernetes_manifests = false`
2. ✓ Run Terraform: `terraform apply`
3. ✓ Make scripts executable: `chmod +x terraform/deploy-docker-and-k8s.sh`
4. ✓ Deploy: `./deploy-docker-and-k8s.sh -e dev -c <ID>`
5. ✓ Verify: `kubectl get pods -n development`

---

## Support

- Full guide: [DEPLOYMENT_GUIDE.md](terraform/DEPLOYMENT_GUIDE.md)
- Architecture: [DEPLOYMENT_ARCHITECTURE_CHANGES.md](DEPLOYMENT_ARCHITECTURE_CHANGES.md)
- Script help: `./deploy-docker-and-k8s.sh --help`
- PowerShell help: `.\deploy-docker-and-k8s.ps1 -Help`

