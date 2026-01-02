# Terraform Deployment Guide

Complete guide covering setup, commands, troubleshooting, and quick reference all in one document.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation & Setup](#installation--setup)
4. [Environment Configuration](#environment-configuration)
5. [Common Commands](#common-commands)
6. [Deployment Workflows](#deployment-workflows)
7. [Troubleshooting](#troubleshooting)
8. [Quick Reference](#quick-reference)

---

## Overview

This Terraform project manages deployment of the AWS Info Website application on Amazon EKS (Elastic Kubernetes Service). It handles:
- AWS provider configuration and authentication
- Kubernetes and Helm provider setup
- Helm chart deployment to EKS cluster
- Multi-environment support (dev, staging, production)

### Project Structure

```
terraform/
├── terraform.tf              # Provider config & version requirements
├── variables.tf              # Input variables with validation
├── outputs.tf                # Output values
├── locals.tf                 # Computed values
├── main.tf                   # Main resources
├── .gitignore               # Git ignore rules
├── environments/             # Environment-specific configs
│   ├── dev.tfvars           # Development
│   ├── staging.tfvars       # Staging
│   └── production.tfvars    # Production
└── modules/eks-deployment/  # Reusable module
    ├── main.tf
    ├── variables.tf
    └── outputs.tf
```

---

## Prerequisites

### Required Software

```bash
# Terraform >= 1.0
terraform version

# AWS CLI
aws --version

# kubectl
kubectl version --client

# Helm (optional, for chart management)
helm version
```

**Installation:**
```bash
# macOS
brew install terraform
brew install awscli
brew install kubectl
brew install helm

# Windows
choco install terraform
choco install awscli
choco install kubernetes-cli
choco install helm

# Linux
curl -fsSL https://apt.releases.hashicorp.com/gpg | apt-key add -
apt-get install terraform
# Install AWS CLI: https://aws.amazon.com/cli/
```

### AWS Account Access

- AWS account with billing enabled
- IAM user/role with appropriate permissions
- EKS cluster already created
- AWS credentials configured
- kubectl configured for the EKS cluster

---

## Installation & Setup

### Step 1: Set Up AWS IAM User

```bash
# Set your AWS region
export AWS_REGION="us-east-1"
export AWS_ACCOUNT_ID="123456789012"  # Your AWS Account ID

# Create IAM user
aws iam create-user --user-name terraform-sa

# Attach required policies
aws iam attach-user-policy --user-name terraform-sa \
  --policy-arn arn:aws:iam::aws:policy/AmazonEKSFullAccess

aws iam attach-user-policy --user-name terraform-sa \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess

aws iam attach-user-policy --user-name terraform-sa \
  --policy-arn arn:aws:iam::aws:policy/IAMUserSSHPublicKeyAccess
```

### Step 2: Create AWS Access Keys

```bash
# Create access keys
aws iam create-access-key --user-name terraform-sa > terraform-credentials.json

# Set restrictive permissions
chmod 600 terraform-credentials.json

# Verify it's in .gitignore
grep "*.json" .gitignore
```

### Step 3: Set Up S3 Buckets for Terraform State

```bash
# Create S3 buckets for each environment
aws s3 mb s3://tf-state-dev-${AWS_ACCOUNT_ID} --region $AWS_REGION
aws s3 mb s3://tf-state-staging-${AWS_ACCOUNT_ID} --region $AWS_REGION
aws s3 mb s3://tf-state-prod-${AWS_ACCOUNT_ID} --region $AWS_REGION

# Enable versioning on all buckets (recommended for state recovery)
aws s3api put-bucket-versioning --bucket tf-state-dev-${AWS_ACCOUNT_ID} --versioning-configuration Status=Enabled
aws s3api put-bucket-versioning --bucket tf-state-staging-${AWS_ACCOUNT_ID} --versioning-configuration Status=Enabled
aws s3api put-bucket-versioning --bucket tf-state-prod-${AWS_ACCOUNT_ID} --versioning-configuration Status=Enabled

# Enable encryption (recommended for security)
aws s3api put-bucket-encryption --bucket tf-state-dev-${AWS_ACCOUNT_ID} --server-side-encryption-configuration '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'
aws s3api put-bucket-encryption --bucket tf-state-staging-${AWS_ACCOUNT_ID} --server-side-encryption-configuration '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'
aws s3api put-bucket-encryption --bucket tf-state-prod-${AWS_ACCOUNT_ID} --server-side-encryption-configuration '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'

# Grant IAM user access to state buckets
TERRAFORM_USER_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:user/terraform-sa"
for bucket in tf-state-dev-${AWS_ACCOUNT_ID} tf-state-staging-${AWS_ACCOUNT_ID} tf-state-prod-${AWS_ACCOUNT_ID}; do
  aws s3api put-bucket-policy --bucket $bucket --policy "{\"Version\": \"2012-10-17\", \"Statement\": [{\"Effect\": \"Allow\", \"Principal\": {\"AWS\": \"${TERRAFORM_USER_ARN}\"}, \"Action\": \"s3:*\", \"Resource\": \"arn:aws:s3:::${bucket}/*\"}]}"
done
```

### Step 4: Verify EKS Cluster

```bash
# List available clusters
aws eks list-clusters --region $AWS_REGION

# Get cluster details
aws eks describe-cluster --name aws-info-website-prod --region $AWS_REGION

# Configure kubectl
aws eks update-kubeconfig --name aws-info-website-prod --region $AWS_REGION

# Verify cluster access
kubectl cluster-info
```

### Step 5: Set Credentials via Environment Variable

**Option A: Set Environment Variable (Recommended)**

PowerShell (Windows):
```powershell
$env:AWS_ACCESS_KEY_ID = "your-access-key-id"
$env:AWS_SECRET_ACCESS_KEY = "your-secret-access-key"
$env:AWS_DEFAULT_REGION = "us-east-1"
```

Bash (Unix/Linux/macOS):
```bash
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_DEFAULT_REGION="us-east-1"
```

**Option B: Use AWS Credentials File**

```bash
aws configure
# Or manually create ~/.aws/credentials file
```

Note: The environment variable approach is recommended as it follows AWS best practices and doesn't require passing credentials on the command line.

### Step 6: Navigate to Terraform Directory

```bash
cd /path/to/aws-info-website
cd terraform
```

### Step 7: Initialize Terraform with GCS Backend

```bash
# For development environment
terraform init -backend-config=environments/backend-dev.tfvars

# For staging environment
terraform init -backend-config=environments/backend-staging.tfvars

# For production environment
terraform init -backend-config=environments/backend-production.tfvars

# Verify initialization
ls -la .terraform/

# Verify state is in S3
aws s3 ls s3://tf-state-dev-${AWS_ACCOUNT_ID}/aws-info-website/terraform/
```

### Step 8: Validate Configuration

```bash
# Check syntax
terraform validate

# Check formatting
terraform fmt -check -recursive

# View formatted files (optional)
terraform fmt -recursive
```

---

## Environment Configuration

### Development Environment

```bash
# Deploy to development (with environment variable set)
# AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY should be set before running
terraform plan -var-file="environments/dev.tfvars" -out=tfplan-dev
terraform apply tfplan-dev

# Verify
terraform output
kubectl get pods -n development
helm list -n development
```

**Configuration (dev.tfvars):**
```hcl
aws_region            = "us-east-1"
environment           = "dev"
cluster_name          = "aws-info-website-dev"
kubernetes_namespace  = "development"
# credentials handled via AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env vars
# Or use AWS_PROFILE for profile-based auth

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
  project     = "aws-info-website"
}
```

### Staging Environment

```bash
# Deploy to staging (mirrors production in structure)
terraform plan -var-file="environments/staging.tfvars" -out=tfplan-staging
terraform apply tfplan-staging
```

### Production Environment

```bash
# ⚠️ PRODUCTION REQUIRES EXTRA CARE

# 1. Review the plan carefully
terraform plan -var-file="environments/production.tfvars" \
  -out=tfplan-prod

# 2. Show detailed plan
terraform show tfplan-prod | less

# 3. Get approval from team

# 4. Apply only when ready
terraform apply tfplan-prod

# 5. Verify thoroughly
terraform output
kubectl get all -n production
helm status mainwebsite -n production
```

---

## Common Commands

### Planning & Validation

```bash
# Validate syntax
terraform validate

# Format check
terraform fmt -check -recursive

# Initialize (first time or after provider changes)
terraform init

# Plan changes (without applying)
terraform plan -var-file="environments/dev.tfvars" -out=tfplan

# Show plan details
terraform show tfplan

# Plan changes with targeting
terraform plan -var-file="environments/dev.tfvars" \
  -target="kubernetes_namespace.default" \
  -out=tfplan
```

### Deployment

```bash
# Set credentials via environment variables first (Recommended)
# PowerShell: $env:AWS_ACCESS_KEY_ID = "your-key"; $env:AWS_SECRET_ACCESS_KEY = "your-secret"
# Bash: export AWS_ACCESS_KEY_ID="your-key"; export AWS_SECRET_ACCESS_KEY="your-secret"

# Apply planned changes
terraform apply tfplan

# Apply with auto-approve (dev only)
terraform apply -auto-approve -var-file="environments/dev.tfvars"

# Apply to production (with review)
terraform apply -var-file="environments/production.tfvars"

# Apply with explicit credentials file (alternative to env var)
terraform apply -var="credentials_file=/path/to/creds.json" -var-file="environments/dev.tfvars"

# Destroy infrastructure (dev only)
terraform destroy -var-file="environments/dev.tfvars"

# Destroy specific resource
terraform destroy -target="kubernetes_namespace.default"
```

### State Management

```bash
# List all resources in current state
terraform state list

# Show resource details from GCS backend
terraform state show 'kubernetes_namespace.default'

# Remove from state (doesn't delete resource, only local tracking)
terraform state rm 'aws_eks_cluster.primary'

# Show all outputs
terraform output

# Get specific output
terraform output -raw gke_cluster_endpoint
terraform output -json | jq '.mainwebsite_namespace'

# Refresh state from GCS backend
terraform refresh

# Backup state from GCS (stored safely in GCS, but good practice)
terraform state pull > terraform.tfstate.backup

# Restore from backup (dangerous - use carefully, updates GCS backend)
terraform state push terraform.tfstate.backup

# Force unlock (if GCS backend lock is stuck)
terraform force-unlock <LOCK_ID>

# List GCS state files
# Verify state is in S3
aws s3 ls s3://tf-state-dev-${AWS_ACCOUNT_ID}/aws-info-website/terraform/ --region $AWS_REGION
```

### Kubernetes Commands

```bash
# Get cluster info
kubectl cluster-info
kubectl get nodes
kubectl get namespaces

# Pod management
kubectl get pods -n production
kubectl describe pod <pod-name> -n production
kubectl logs <pod-name> -n production
kubectl logs <pod-name> -n production --previous  # Crashed pod
kubectl exec -it <pod-name> -n production -- /bin/bash

# Troubleshooting
kubectl get events -n production
kubectl describe node <node-name>
kubectl top pods -n production
kubectl top nodes

# Resource management
kubectl delete pod <pod-name> -n production --grace-period=0 --force
kubectl scale deployment <deployment-name> --replicas=3 -n production

# Port forwarding
kubectl port-forward -n production svc/mainwebsite 8080:80
```

### Helm Commands

```bash
# List releases
helm list -n production

# Get release values
helm get values mainwebsite -n production

# Show deployed manifest
helm get manifest mainwebsite -n production

# Check release status
helm status mainwebsite -n production

# View release history
helm history mainwebsite -n production

# Rollback to previous version
helm rollback mainwebsite -n production

# Dry-run deployment
helm install test ../helm-dir --dry-run --debug

# Validate chart
helm lint ../helm-dir/
```

### AWS Commands

```bash
# List clusters
aws eks list-clusters --region us-east-1

# Get cluster details
aws eks describe-cluster --name CLUSTER_NAME --region REGION

# Configure kubectl
aws eks update-kubeconfig --name CLUSTER_NAME --region REGION

# Check IAM permissions
aws iam list-user-policies --user-name USERNAME

# View logs
aws logs describe-log-groups
aws logs tail /aws/eks/cluster/CLUSTER_NAME --follow

# Test authentication
aws sts get-caller-identity
aws configure list
```

---

## Deployment Workflows

### Quick Dev Deployment (5 minutes)

```bash
cd terraform

# Set credentials environment variables first
# PowerShell: $env:AWS_ACCESS_KEY_ID = "your-key"; $env:AWS_SECRET_ACCESS_KEY = "your-secret"
# Bash: export AWS_ACCESS_KEY_ID="your-key"; export AWS_SECRET_ACCESS_KEY="your-secret"

# Initialize with S3 backend
terraform init -backend-config=environments/backend-dev.tfvars

# Plan and apply
terraform plan -var-file="environments/dev.tfvars"
terraform apply -var-file="environments/dev.tfvars"
terraform output
```

### Production Deployment (with Review - 20 minutes)

```bash
# 1. Plan
terraform plan -var-file="environments/production.tfvars" -out=tfplan

# 2. Review
terraform show tfplan

# 3. Get approval from team

# 4. Apply
terraform apply tfplan

# 5. Verify
terraform output
kubectl get all -n production

# 6. Verify state is in S3
aws s3 ls s3://tf-state-prod-${AWS_ACCOUNT_ID}/aws-info-website/terraform/ --region $AWS_REGION
```

### Rollback

```bash
# Option 1: Revert tfvars and redeploy
git checkout environments/production.tfvars
terraform apply -var-file="environments/production.tfvars"

# Option 2: Helm rollback
helm rollback mainwebsite -n production

# Option 3: Restore from S3 versioned state
# First, list versions
aws s3api list-object-versions --bucket tf-state-prod-${AWS_ACCOUNT_ID} --prefix aws-info-website/terraform/ --region $AWS_REGION
# Then restore specific version
aws s3api get-object --bucket tf-state-prod-${AWS_ACCOUNT_ID} --key aws-info-website/terraform/default.tfstate --version-id <VERSION_ID> restore.tfstate
```

### Scaling

```bash
# Scale replicas
terraform apply -var-file="environments/production.tfvars" \
  -var="helm_set_values={\"mainwebsite.replicaCount\" = \"5\"}"

# Or update tfvars file and redeploy
nano environments/production.tfvars
terraform apply -var-file="environments/production.tfvars"
```

---

## Troubleshooting

### Provider & Authentication Issues

#### Error: "Error configuring the AWS Provider"

**Symptoms:**
```
Error: Error configuring the AWS Provider: No valid credential sources found
```

**Solutions:**
```bash
# Option 1: Set environment variable (RECOMMENDED)
# PowerShell: 
$env:AWS_ACCESS_KEY_ID = "your-access-key-id"
$env:AWS_SECRET_ACCESS_KEY = "your-secret-access-key"
$env:AWS_DEFAULT_REGION = "us-east-1"

# Bash:
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_DEFAULT_REGION="us-east-1"

# Then run Terraform
terraform plan -var-file="environments/dev.tfvars"

# Option 2: Use AWS credentials file
aws configure

# Option 3: Use AWS profiles
export AWS_PROFILE=terraform-sa
terraform plan -var-file="environments/dev.tfvars"

# Verify credentials are accessible
aws sts get-caller-identity
```

#### Error: "Error requesting list of clusters"

**Symptoms:**
```
Error: Error requesting list of clusters: Access Denied
```

**Solution:**
```bash
# Grant required permissions to IAM user
aws iam attach-user-policy --user-name terraform-sa \
  --policy-arn arn:aws:iam::aws:policy/AmazonEKSFullAccess

aws iam attach-user-policy --user-name terraform-sa \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess

# Verify permissions
aws iam list-user-policies --user-name terraform-sa
```

### S3 Backend State Issues

#### Error: "Error reading state from backend"

**Cause:** S3 bucket doesn't exist or IAM user lacks permissions

**Solution:**
```bash
# Verify bucket exists
aws s3 ls s3://tf-state-dev-${AWS_ACCOUNT_ID}/ --region $AWS_REGION

# Create bucket if missing
aws s3 mb s3://tf-state-dev-${AWS_ACCOUNT_ID} --region $AWS_REGION

# Grant IAM user access
USER_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:user/terraform-sa"
aws s3api put-bucket-policy --bucket tf-state-dev-${AWS_ACCOUNT_ID} \
  --policy '{"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": {"AWS": "'${USER_ARN}'"}, "Action": "s3:*", "Resource": "arn:aws:s3:::tf-state-dev-'${AWS_ACCOUNT_ID}'/*"}]}'

# Reinitialize backend
terraform init -backend-config=environments/backend-dev.tfvars
```

#### Error: "Error acquiring the state lock"

**Cause:** Another operation is using the state file or lock is stuck

**Solution:**
```bash
# Wait for other operations to complete
# If stuck, force unlock (use with caution):
terraform force-unlock <LOCK_ID>

# List locks in S3 (if DynamoDB table is used for locking):
aws dynamodb scan --table-name terraform-locks --region $AWS_REGION
```

#### Error: "Error: Error requesting list of clusters"

**Symptoms:**
```
Error: Error requesting list of clusters: Access Denied
```

**Solution:**
```bash
# Grant required permissions to IAM user
USER_ARN="arn:aws:iam::ACCOUNT_ID:user/terraform-sa"

# Attach EKS and EC2 policies
aws iam attach-user-policy --user-name terraform-sa \
  --policy-arn arn:aws:iam::aws:policy/AmazonEKSFullAccess

# Verify permissions
aws iam list-attached-user-policies --user-name terraform-sa
```

#### Error: "Error: Invalid or unsupported attribute name"

**Cause:** Incorrect resource attribute

**Solution:**
```bash
# Validate syntax
terraform validate

# Format code
terraform fmt -recursive

# Check provider documentation
terraform providers
# https://registry.terraform.io/providers/hashicorp/aws/latest
```

### Kubernetes Connection Issues

#### Error: "Error: Unable to connect to Kubernetes cluster"

**Solution:**
```bash
# Configure kubeconfig
aws eks update-kubeconfig --name aws-info-website-prod --region us-east-1

# Test connectivity
kubectl cluster-info
kubectl get nodes
kubectl auth can-i create pods
```

#### Error: "Error: Unable to authenticate with Kubernetes"

**Solution:**
```bash
# Regenerate kubeconfig
aws eks update-kubeconfig --name aws-info-website-prod --region us-east-1

# Verify context
kubectl config current-context
kubectl config get-contexts

# Test
kubectl get namespaces
```

### Helm & Chart Issues

#### Error: "Error: chart not found"

**Cause:** Incorrect chart path

**Solution:**
```bash
# Verify chart exists
ls -la ../helm-dir/Chart.yaml

# Validate chart
helm lint ../helm-dir/

# Update path in tfvars
echo 'helm_chart_path = "/full/path/to/helm-dir"' >> environments/dev.tfvars

# Test dry-run
helm install test /path/to/helm-dir/ --dry-run
```

#### Error: "ImagePullBackOff"

**Cause:** Image doesn't exist or registry auth failed

**Solution:**
```bash
# Verify image exists
aws ecr describe-images --repository-name mainwebsite --region us-east-1

# Check image tag
terraform output -raw mainwebsite_image_tag

# Update tfvars
echo 'mainwebsite_image_tag = "v1.0.0"' >> environments/dev.tfvars

# Verify registry access
aws ecr describe-images --repository-name image --region us-east-1
```

#### Error: "CrashLoopBackOff"

**Cause:** Application error or configuration issue

**Solution:**
```bash
# Check pod logs
kubectl logs <pod-name> -n production -c <container>

# Previous crash logs
kubectl logs <pod-name> -n production --previous

# Describe pod for events
kubectl describe pod <pod-name> -n production

# Check environment variables
kubectl get pod <pod-name> -n production -o yaml | grep -A20 env:

# Check resource allocation
kubectl top pods -n production
```

### Terraform State Issues

#### Error: "Error acquiring the state lock"

**Solution:**
```bash
# List state locks
terraform force-unlock <LOCK_ID>

# Backup state
cp terraform.tfstate terraform.tfstate.backup

# Refresh state
terraform refresh

# Validate state
terraform validate
```

#### Error: "State has uncommitted resource changes"

**Solution:**
```bash
# Apply pending changes
terraform apply -auto-approve

# Or refresh
terraform refresh

# Or manually inspect
terraform state list
terraform state show <resource>
```

### Resource Issues

#### Error: "Insufficient memory"

**Solution:**
```bash
# Check node capacity
kubectl top nodes

# Increase resource requests
# Edit tfvars to increase memory:
echo 'helm_set_values = {"mainwebsite.resources.requests.memory" = "512Mi"}' >> environments/dev.tfvars

# Or scale cluster
aws eks update-nodegroup-config --cluster-name aws-info-website-prod --nodegroup-name default --scaling-config minSize=1,maxSize=5,desiredSize=5 --region us-east-1
```

#### Error: "Insufficient CPU"

**Solution:**
```bash
# Check CPU allocation
kubectl top nodes

# Reduce CPU requests in tfvars
# Or add node group with higher compute
aws eks create-nodegroup --cluster-name aws-info-website-prod --nodegroup-name high-cpu \
  --scaling-config minSize=1,maxSize=5,desiredSize=2 \
  --subnets subnet-xxxxx subnet-yyyyy --node-role arn:aws:iam::ACCOUNT:role/NodeInstanceRole \
  --instance-types c5.2xlarge --region us-east-1
```

### Timeout Issues

#### Error: "Timeout while waiting for Helm release to be active"

**Cause:** Pods not starting, resource constraints, or long initialization

**Solution:**
```bash
# Check pod status
kubectl get pods -n production

# View pod events
kubectl get events -n production --sort-by='.lastTimestamp'

# Check logs
kubectl logs <pod-name> -n production
kubectl logs <pod-name> -n production --previous

# Increase timeout in tfvars
echo 'helm_timeout = 600' >> environments/production.tfvars

# Check node status
kubectl describe node
```

### Common Configuration Issues

| Issue | Solution |
|-------|----------|
| Credentials not found | Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env vars |
| Permission denied | Add IAM roles to service account |
| Cluster not found | Verify cluster_name and region |
| Chart not found | Check helm_chart_path in tfvars |
| Pod not starting | Check logs: `kubectl logs <pod> -n namespace` |
| Helm timeout | Increase helm_timeout in tfvars |
| State locked | Use `terraform force-unlock <LOCK_ID>` |
| Invalid attribute | Run `terraform validate` and check spelling |
| S3 bucket not found | Create bucket with `aws s3 mb` and reinit backend |

### Debugging Workflow

```bash
# 1. Enable debug logging
$env:TF_LOG = "DEBUG"  # PowerShell
# export TF_LOG=DEBUG   # Bash

# 2. Verify credentials are set
aws sts get-caller-identity
aws configure list

# 3. Run failing command
terraform plan -var-file="environments/dev.tfvars"

# 4. Check Terraform state location
terraform state list

# 5. Check Kubernetes resources
kubectl get all -n production

# 6. Check Helm release
helm status mainwebsite -n production

# 7. Check logs
kubectl logs -n production -l app=mainwebsite

# 8. Disable debugging
$env:TF_LOG = ""  # PowerShell
# export TF_LOG=  # Bash
```

### Emergency Procedures

```bash
# Force delete stuck pod
kubectl delete pod <pod-name> -n production --grace-period=0 --force

# Force delete stuck deployment
kubectl delete deployment <deployment-name> -n production --cascade=orphan

# Terraform force unlock (releases GCS lock)
terraform force-unlock <LOCK_ID>

# Emergency destroy (dev/staging only)
terraform destroy -auto-approve -var-file="environments/dev.tfvars"

# Restore from S3 backup (if versioning enabled)
aws s3api get-object --bucket tf-state-prod-${AWS_ACCOUNT_ID} --key aws-info-website/terraform/default.tfstate --version-id <VERSION_ID> restore.tfstate
terraform state push restore.tfstate
```

---

## Quick Reference

### Environment Variables

```bash
# AWS
export AWS_REGION="us-east-1"
export AWS_ACCOUNT_ID="123456789012"

# Credentials (RECOMMENDED - set before Terraform)
# PowerShell:
$env:AWS_ACCESS_KEY_ID = "your-access-key"
$env:AWS_SECRET_ACCESS_KEY = "your-secret-key"

# Bash:
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"

# Terraform
$env:TF_LOG = "DEBUG"           # PowerShell - Enable debug logging
# export TF_LOG=DEBUG           # Bash
$env:TF_INPUT = "false"          # PowerShell - Don't prompt for input
# export TF_INPUT=false          # Bash
$env:TF_VAR_project_id = "..."   # PowerShell - Override variables
# export TF_VAR_project_id="..." # Bash

# Kubernetes & AWS
$env:KUBECONFIG = "$HOME\.kube\config"  # PowerShell
# export KUBECONFIG=~/.kube/config      # Bash
$env:KUBE_NAMESPACE = "production"       # PowerShell
# export KUBE_NAMESPACE=production       # Bash
$env:AWS_PROFILE = "terraform-sa"        # PowerShell (optional)
# export AWS_PROFILE=terraform-sa        # Bash (optional)

# Helm
$env:HELM_TIMEOUT = "600"  # PowerShell
# export HELM_TIMEOUT=600   # Bash
```

### Configuration Reference

| Variable | Dev | Staging | Prod |
|----------|-----|---------|------|
| Image Tag | dev-latest | staging-latest | v1.0.0 |
| Replicas | 1 | 2 | 3 |
| Autoscaling | No | Yes | Yes |
| Timeout | 300s | 300s | 600s |
| Atomic | true | true | true |
| State Bucket | tf-state-dev-${ACCOUNT_ID} | tf-state-staging-${ACCOUNT_ID} | tf-state-prod-${ACCOUNT_ID} |

### Key Outputs

```bash
# View all outputs
terraform output

# GKE cluster endpoint
terraform output -raw gke_cluster_endpoint

# Kubernetes namespace
terraform output -raw mainwebsite_namespace

# List state files in S3
aws s3 ls s3://tf-state-dev-${AWS_ACCOUNT_ID}/aws-info-website/terraform/

# List state files in S3
aws s3 ls s3://tf-state-dev-${AWS_ACCOUNT_ID}/aws-info-website/terraform/

# Helm release status
terraform output -raw helm_release_status
```

### Security Checklist

✅ **DO:**
- Use version tags in production (v1.0.0, never latest)
- Mark sensitive variables
- Keep credentials in .gitignore
- Backup state regularly
- Use remote state (GCS) in production
- Review plans before apply
- Use service accounts
- Restrict IAM permissions

❌ **DON'T:**
- Commit credentials or state files
- Use "latest" in production
- Deploy without planning
- Force destroy in production
- Hardcode secrets
- Use personal credentials
- Skip validation
- Ignore warnings/errors

### Troubleshooting Checklist

- [ ] Verify authentication: `aws sts get-caller-identity`
- [ ] Check cluster access: `kubectl cluster-info`
- [ ] Verify credentials file: `ls -la credentials.json`
- [ ] Validate Terraform: `terraform validate`
- [ ] Review plan before apply: `terraform show tfplan`
- [ ] Check pod status: `kubectl get pods -n production`
- [ ] View pod logs: `kubectl logs <pod> -n production`
- [ ] Check Helm release: `helm status mainwebsite -n production`
- [ ] Check resource allocation: `kubectl top pods -n production`

---

## Remote State Setup (Recommended for Teams)

### Create S3 Bucket for State

```bash
# Create bucket
aws s3 mb s3://${AWS_ACCOUNT_ID}-terraform-state --region $AWS_REGION

# Enable versioning
aws s3api put-bucket-versioning --bucket ${AWS_ACCOUNT_ID}-terraform-state \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption --bucket ${AWS_ACCOUNT_ID}-terraform-state \
  --server-side-encryption-configuration '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'

# Set lifecycle policy (keep last 5 versions)
aws s3api put-bucket-lifecycle-configuration --bucket ${AWS_ACCOUNT_ID}-terraform-state \
  --lifecycle-configuration '{
    "Rules": [{
      "Status": "Enabled",
      "NoncurrentVersionExpirationInDays": 7,
      "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 7}
    }]
  }'

# Block public access
aws s3api put-public-access-block --bucket ${AWS_ACCOUNT_ID}-terraform-state \
  --public-access-block-configuration \
  "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

### Enable Backend

```hcl
# In terraform.tf, uncomment:
terraform {
  backend "s3" {
    bucket         = "your-account-id-terraform-state"
    key            = "aws-info-website/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}
```

### Migrate State

```bash
# Create DynamoDB table for state locking (optional but recommended)
aws dynamodb create-table \
  --table-name terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
  --region $AWS_REGION

# Terraform will prompt to migrate
terraform init

# Confirm migration
# Local state backed up to terraform.tfstate.backup
```

---

## Additional Resources

- [Terraform Documentation](https://www.terraform.io/docs)
- [AWS Provider Docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Kubernetes Provider Docs](https://registry.terraform.io/providers/hashicorp/kubernetes/latest/docs)
- [Helm Provider Docs](https://registry.terraform.io/providers/hashicorp/helm/latest/docs)
- [EKS Documentation](https://docs.aws.amazon.com/eks/)
- [AWS CLI Documentation](https://docs.aws.amazon.com/cli/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Helm Documentation](https://helm.sh/docs/)

---

**Last Updated**: January 2, 2026  
**Status**: Production-Ready
