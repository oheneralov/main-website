#!/bin/bash

################################################################################
# DEPLOYMENT GUIDE: Separating Infrastructure and Kubernetes Deployment
################################################################################

This guide explains how to use Terraform for infrastructure provisioning and
the deploy-docker-and-k8s.sh script for container builds and Kubernetes deployment.

## Overview

Previously, Kubernetes manifests were deployed during `terraform apply`. This approach
has been separated into two distinct phases:

1. **Infrastructure Phase (Terraform)**: Creates AWS resources (VPC, EKS cluster, etc.)
2. **Application Phase (Shell Script)**: Builds Docker images, pushes to ECR, and deploys K8s manifests

## Benefits

- ✓ Faster iteration on application deployments without reprovisioning infrastructure
- ✓ Independent Docker image builds and ECR pushes
- ✓ Separation of concerns: infrastructure vs application deployment
- ✓ Better CI/CD pipeline integration
- ✓ Easy rollback of application changes without affecting infrastructure
- ✓ Flexible deployment: skip Docker or K8s phases independently

## Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform >= 1.0
- Docker
- kubectl
- Helm
- AWS Account with ECR access
- EKS Cluster (created by Terraform)

## Deployment Workflow

### Phase 1: Infrastructure Provisioning (Terraform)

#### 1. Prepare Terraform Variables

Create or update your environment variables file (e.g., `dev.tfvars`):

```hcl
region                          = "us-east-1"
environment                     = "dev"
cluster_name                    = "my-eks-cluster"
kubernetes_version              = "1.28"
node_group_min_size             = 2
node_group_max_size             = 5
node_group_desired_size         = 3

# IMPORTANT: Set this to false to skip Kubernetes deployment during terraform apply
deploy_kubernetes_manifests     = false

# Other variables...
kubernetes_namespace            = "development"
helm_chart_path                 = "../helm-dir"
```

#### 2. Initialize and Plan Terraform

```bash
cd terraform

# Initialize Terraform (if not already done)
terraform init -backend-config="bucket=your-state-bucket" \
               -backend-config="key=aws-info-website/terraform.state"

# Plan the deployment
terraform plan -var-file="environments/dev.tfvars" -out=tfplan
```

#### 3. Apply Infrastructure

```bash
terraform apply tfplan
```

This creates all AWS infrastructure (VPC, EKS cluster, node groups, IAM roles, etc.)
but skips Kubernetes manifest deployment due to `deploy_kubernetes_manifests = false`.

#### 4. Configure kubectl Access

After Terraform completes, configure kubectl to access the new cluster:

```bash
# Update kubeconfig
aws eks update-kubeconfig --region us-east-1 --name my-eks-cluster

# Verify cluster access
kubectl get nodes
```

### Phase 2: Application Deployment (Shell Script)

#### 1. Make Script Executable

```bash
chmod +x terraform/deploy-docker-and-k8s.sh
```

#### 2. Deploy with All Phases

Build Docker images, push to ECR, and deploy Kubernetes manifests:

```bash
./terraform/deploy-docker-and-k8s.sh \
  --environment dev \
  --registry-id 123456789012 \
  --region us-east-1 \
  --namespace development
```

#### 3. Alternative: Skip Docker Phase (Use Existing Images)

Only deploy Kubernetes manifests with existing ECR images:

```bash
./terraform/deploy-docker-and-k8s.sh \
  --environment dev \
  --namespace development \
  --skip-docker
```

#### 4. Alternative: Skip Kubernetes Phase (Only Build Docker)

Build and push Docker images without deploying to Kubernetes:

```bash
./terraform/deploy-docker-and-k8s.sh \
  --environment dev \
  --registry-id 123456789012 \
  --region us-east-1 \
  --skip-k8s
```

## Script Usage Details

### Full Command Syntax

```bash
./deploy-docker-and-k8s.sh [OPTIONS]
```

### Options

| Option | Short | Description | Required |
|--------|-------|-------------|----------|
| `--environment` | `-e` | Environment (dev, staging, production) | Yes |
| `--registry-id` | `-c` | AWS Account ID for ECR | When not skipping Docker |
| `--region` | `-r` | AWS region (default: us-east-1) | No |
| `--namespace` | `-n` | Kubernetes namespace (default: development) | No |
| `--helm-chart-path` | `-h` | Path to Helm chart (default: ../helm-dir) | No |
| `--skip-docker` | `-s` | Skip Docker build and push | No |
| `--skip-k8s` | `-k` | Skip Kubernetes deployment | No |
| `--help` | | Display help message | No |

### Examples

```bash
# Full deployment for production
./deploy-docker-and-k8s.sh \
  -e production \
  -c 123456789012 \
  -r us-east-1 \
  -n production

# Dev environment with defaults
./deploy-docker-and-k8s.sh -e dev -c 123456789012

# Only apply K8s manifests (skip Docker)
./deploy-docker-and-k8s.sh -e staging -s

# Only build and push Docker (skip K8s)
./deploy-docker-and-k8s.sh -e dev -c 123456789012 -k

# Custom Helm chart path
./deploy-docker-and-k8s.sh -e dev -c 123456789012 \
  -h /custom/helm/chart/path
```

## Script Features

### Docker Image Building

- Builds Docker images from Dockerfiles in:
  - `mainwebsite/Dockerfile`
  - `metrics/Dockerfile` (if exists)
- Tags images with `:latest`
- Creates timestamped tags (e.g., `20240113-143025`)

### ECR Push

- Authenticates with Amazon ECR using AWS credentials
- Tags and pushes both `:latest` and timestamped versions
- Supports rolling back to previous versions using timestamps

### Kubernetes Deployment

- Creates the specified namespace if it doesn't exist
- Uses base Helm values from `values.yaml`
- Applies environment-specific values from `values-{environment}.yaml`
- Updates image references with ECR registry URLs
- Verifies deployment with rollout status
- Displays pod and service information

## Updating deploy_kubernetes_manifests Variable

### To Enable K8s Deployment in Terraform Again

If you want to revert to deploying Kubernetes manifests via Terraform, update your
variable file:

```hcl
deploy_kubernetes_manifests = true
```

Then run:

```bash
terraform apply -var-file="environments/dev.tfvars"
```

### Per-Environment Configuration

Set `deploy_kubernetes_manifests` differently for each environment:

**environments/dev.tfvars**:
```hcl
deploy_kubernetes_manifests = false  # Use script for dev
```

**environments/production.tfvars**:
```hcl
deploy_kubernetes_manifests = false  # Use script for production
```

## Troubleshooting

### Docker Build Fails

```bash
# Check Docker daemon is running
docker ps

# Verify Dockerfile exists
ls -la mainwebsite/Dockerfile

# Build with verbose output
docker build -f mainwebsite/Dockerfile -t mainwebsite:latest mainwebsite --progress=plain
```

### ECR Authentication Fails

```bash
# Verify AWS credentials
aws sts get-caller-identity

# Check ECR repository exists
aws ecr describe-repositories --region us-east-1

# Manual ECR login
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
```

### Kubernetes Deployment Fails

```bash
# Verify kubectl access
kubectl get nodes

# Check namespace
kubectl get namespaces

# View Helm releases
helm list -A

# Check deployment status
kubectl get deployment -n development

# View deployment logs
kubectl logs deployment/mainwebsite -n development

# Describe pod for errors
kubectl describe pod -n development
```

### Helm Chart Not Found

```bash
# Verify chart path is correct
ls -la ../helm-dir/

# Check Chart.yaml exists
cat ../helm-dir/Chart.yaml

# Verify values files exist
ls -la ../helm-dir/values*.yaml
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v1
      
      - name: Deploy Infrastructure
        working-directory: terraform
        run: |
          terraform init
          terraform plan -var-file="environments/prod.tfvars" -out=tfplan
          terraform apply tfplan
      
      - name: Deploy Applications
        run: |
          chmod +x terraform/deploy-docker-and-k8s.sh
          ./terraform/deploy-docker-and-k8s.sh \
            -e production \
            -c ${{ secrets.AWS_ACCOUNT_ID }} \
            -r us-east-1
```

### GitLab CI/CD Example

```yaml
stages:
  - infrastructure
  - application

terraform_apply:
  stage: infrastructure
  image: hashicorp/terraform:latest
  script:
    - cd terraform
    - terraform init
    - terraform plan -var-file="environments/prod.tfvars" -out=tfplan
    - terraform apply tfplan
  only:
    - main

deploy_application:
  stage: application
  image: docker:latest
  services:
    - docker:dind
  script:
    - chmod +x terraform/deploy-docker-and-k8s.sh
    - ./terraform/deploy-docker-and-k8s.sh -e production -c ${AWS_ACCOUNT_ID}
  dependencies:
    - terraform_apply
  only:
    - main
```

## Rollback Procedures

### Rollback Application (Kubernetes Only)

```bash
# View Helm release history
helm history mainwebsite -n development

# Rollback to previous release
helm rollback mainwebsite -n development

# Rollback to specific revision
helm rollback mainwebsite 3 -n development
```

### Rollback Docker Image

```bash
# Use timestamped image tag
docker pull 123456789012.dkr.ecr.us-east-1.amazonaws.com/mainwebsite:20240113-143025

# Update Helm values with specific tag
./deploy-docker-and-k8s.sh -e dev -s  # Skip Docker, only deploy K8s
# Then manually update image tag in values or use helm upgrade
```

## Best Practices

1. **Always backup your state**: Configure S3 backend with versioning and DynamoDB locks
2. **Use environment variables**: Store sensitive data in secure vaults, not in code
3. **Test in dev first**: Always validate changes in development before production
4. **Namespace isolation**: Use different namespaces for different environments
5. **Image versioning**: Use specific image tags in production, not just `:latest`
6. **Monitoring**: Verify deployments with pod logs and metrics
7. **Git workflows**: Use branches and pull requests for infrastructure changes
8. **Documentation**: Keep deployment runbooks updated

## Additional Resources

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Kubernetes Helm Charts](https://helm.sh/docs/)
- [Amazon ECR Documentation](https://docs.aws.amazon.com/ecr/)
- [EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)

