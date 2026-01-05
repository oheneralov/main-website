# Terraform Setup Guide

## Prerequisites

Before you begin, ensure you have:

### 1. Required Software
```bash
# Terraform >= 1.0
terraform version

# gcloud CLI
gcloud --version

# kubectl
kubectl version --client

# Helm (optional, for chart management)
helm version
```

### 2. GCP Account Setup

#### Create Service Account
```bash
# Set your project
export PROJECT_ID="clever-spirit-417020"
gcloud config set project $PROJECT_ID

# Create service account
gcloud iam service-accounts create terraform-sa \
  --display-name="Terraform Service Account"

# Grant necessary roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:terraform-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/container.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:terraform-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/compute.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:terraform-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

#### Create Service Account Key
```bash
# Create JSON key
gcloud iam service-accounts keys create \
  clever-spirit-terraform-service-account.json \
  --iam-account=terraform-sa@${PROJECT_ID}.iam.gserviceaccount.com

# Make it readable only by you
chmod 600 clever-spirit-terraform-service-account.json
```

### 3. GKE Cluster Verification

```bash
# List available clusters
gcloud container clusters list

# Get cluster details
gcloud container clusters describe gcp-info-website-prod \
  --region us-central1

# Configure kubectl
gcloud container clusters get-credentials gcp-info-website-prod \
  --region us-central1

# Verify cluster access
kubectl cluster-info
```

---

## Installation Steps

### Step 1: Clone/Download Project

```bash
cd /path/to/gcp-info-website
cd terraform
```

### Step 2: Place Service Account Credentials

```bash
# Copy or create credentials file
cp /path/to/service-account-key.json ./clever-spirit-terraform-service-account.json

# Verify file is in .gitignore (should NOT be committed)
grep "*.json" .gitignore
```

### Step 3: Initialize Terraform

```bash
# Download providers
terraform init

# Verify initialization
ls -la .terraform/
```

### Step 4: Validate Configuration

```bash
# Check syntax
terraform validate

# Check formatting
terraform fmt -check -recursive
```

### Step 5: Plan Deployment

```bash
# For development
terraform plan -var-file="environments/dev.tfvars" -out=tfplan-dev

# For staging
terraform plan -var-file="environments/staging.tfvars" -out=tfplan-staging

# For production
terraform plan -var-file="environments/production.tfvars" -out=tfplan-prod
```

### Step 6: Apply Configuration

```bash
# Development (safe to test)
terraform apply tfplan-dev

# Production (requires caution)
terraform apply tfplan-prod
```

### Step 7: Verify Deployment

```bash
# Get outputs
terraform output

# Get specific output
terraform output gke_cluster_endpoint

# Check Helm release
helm list -n <namespace>

# Check pods
kubectl get pods -n <namespace>
```

---

## Environment Setup

### Development Environment

```bash
# Copy dev configuration
cp environments/dev.tfvars.example environments/dev.tfvars

# Edit as needed
nano environments/dev.tfvars

# Deploy
terraform apply -var-file="environments/dev.tfvars"
```

### Staging Environment

```bash
# Staging typically mirrors production in structure
terraform apply -var-file="environments/staging.tfvars"
```

### Production Environment

```bash
# PRODUCTION REQUIRES EXTRA CARE

# 1. Review the plan carefully
terraform plan -var-file="environments/production.tfvars" \
  -out=tfplan-prod

# 2. Show detailed plan
terraform show tfplan-prod | less

# 3. Apply only when ready
terraform apply tfplan-prod
```

---

## Remote State Setup (Recommended for Teams)

### Create GCS Bucket for State

```bash
# Create bucket
gsutil mb gs://${PROJECT_ID}-terraform-state

# Enable versioning
gsutil versioning set on gs://${PROJECT_ID}-terraform-state

# Set lifecycle policy
gsutil lifecycle set - <<EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"numNewerVersions": 5}
      }
    ]
  }
}
EOF

# Restrict access
gsutil acl ch -u terraform-sa@${PROJECT_ID}.iam.gserviceaccount.com \
  gs://${PROJECT_ID}-terraform-state
```

### Enable Backend in terraform.tf

```hcl
backend "gcs" {
  bucket  = "your-project-id-terraform-state"
  prefix  = "gcp-info-website"
}
```

### Migrate State

```bash
# Terraform will prompt to migrate state
terraform init

# Confirm migration
# Local state will be backed up to terraform.tfstate.backup
```

---

## Configuration File Template

### Create environments/dev.tfvars

```hcl
project_id            = "clever-spirit-417020"
region                = "us-central1"
environment           = "dev"
cluster_name          = "gcp-info-website-dev"
kubernetes_namespace  = "development"
credentials_file      = "./clever-spirit-terraform-service-account.json"

helm_chart_path       = "../helm-dir"
helm_release_name     = "mainwebsite"
helm_timeout          = 300
helm_atomic_deployment = true

mainwebsite_image_tag = "dev-latest"
metrics_image_tag     = "dev-latest"

helm_set_values = {
  "mainwebsite.replicaCount" = "1"
  "metrics.replicaCount"     = "1"
}

common_labels = {
  environment = "dev"
  managed_by  = "terraform"
  project     = "gcp-info-website"
}
```

---

## Troubleshooting Setup

### Provider Authentication Issues

```bash
# Test GCP authentication
gcloud auth application-default login

# List credentials
gcloud config list

# Check service account permissions
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --format="table(bindings.role)" \
  --filter="bindings.members:terraform-sa@*"
```

### Kubernetes Connection Issues

```bash
# Test cluster connectivity
kubectl cluster-info

# Get cluster endpoint
gcloud container clusters describe <cluster-name> \
  --region us-central1 \
  --format="value(endpoint)"

# Test API access
kubectl auth can-i create deployments
```

### Helm Issues

```bash
# Validate chart
helm lint ../helm-dir/

# Dry-run Helm
helm install mainwebsite ../helm-dir/ --dry-run --debug

# Check Helm repositories
helm repo list
```

---

## Common Configuration Issues

### Issue: "Error: credentials file not found"

**Solution**: 
```bash
# Copy credentials to terraform directory
cp /path/to/key.json ./clever-spirit-terraform-service-account.json

# Or update path in environments/*.tfvars
credentials_file = "/full/path/to/key.json"
```

### Issue: "Error: accessing gke cluster - permission denied"

**Solution**:
```bash
# Grant additional permissions to service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:terraform-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/container.developer"
```

### Issue: "Error: helm chart not found"

**Solution**:
```bash
# Verify chart path
ls -la ../helm-dir/Chart.yaml

# Update helm_chart_path in environments/*.tfvars
helm_chart_path = "/full/path/to/helm-dir"
```

---

## Security Best Practices

### Credentials Security
```bash
# Set restrictive permissions
chmod 600 clever-spirit-terraform-service-account.json

# Verify it's in .gitignore
grep "*.json" .gitignore

# Never commit credentials
git status  # Should not show JSON file
```

### State File Security
```bash
# Local state contains sensitive data
chmod 600 terraform.tfstate

# Use remote state in production
# Configure GCS backend with encryption
```

### Variable Security
```bash
# Never hardcode sensitive values
# Use tfvars files marked as sensitive

# Sensitive variables in code
sensitive = true

# Example:
variable "credentials_file" {
  sensitive = true
}
```

---

## Verification Checklist

- [ ] Terraform >= 1.0 installed
- [ ] gcloud CLI configured
- [ ] kubectl configured and working
- [ ] Service account created with proper roles
- [ ] Service account key downloaded
- [ ] Key file in terraform directory
- [ ] Key file in .gitignore
- [ ] terraform init successful
- [ ] terraform validate passes
- [ ] Plan generated successfully
- [ ] Ready for terraform apply

---

## Next Steps

1. **Development**: Deploy to dev environment and test
2. **Staging**: Deploy to staging and verify in production-like environment
3. **Production**: Deploy to production with appropriate approvals
4. **Monitoring**: Set up monitoring and alerting
5. **Automation**: Consider CI/CD pipeline for deployments

---

## Getting Help

If you encounter issues:
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review [BEST_PRACTICES.md](BEST_PRACTICES.md)
3. Check provider documentation:
   - [GCP Provider](https://registry.terraform.io/providers/hashicorp/google/latest)
   - [Kubernetes Provider](https://registry.terraform.io/providers/hashicorp/kubernetes/latest)
   - [Helm Provider](https://registry.terraform.io/providers/hashicorp/helm/latest)
4. Review GKE and Helm documentation

---

**Last Updated**: January 2, 2026
