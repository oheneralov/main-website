# Terraform Infrastructure-as-Code

Infrastructure-as-code configuration for deploying the AWS Info Website on Amazon EKS (Elastic Kubernetes Service). This Terraform module manages the complete infrastructure including EKS cluster provisioning, Kubernetes provider configuration, and Helm chart deployments.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)

---

## Overview

### What This Terraform Module Does

- **EKS Cluster Integration**: Manages connection and authentication to existing Amazon EKS clusters
- **Multi-Environment Support**: Handles dev, staging, and production environments with environment-specific variables
- **Helm Deployments**: Deploys the mainwebsite and associated services using Helm charts
- **State Management**: Configurable remote state storage in AWS S3
- **Infrastructure Automation**: Fully reproducible infrastructure deployments

### Architecture

```
AWS Account
├── EKS Cluster (existing or managed)
│   ├── Kubernetes Namespace (configurable)
│   └── Helm Releases
│       ├── mainwebsite (primary application)
│       └── metrics (monitoring service)
├── S3 (Terraform state backend)
└── Other AWS Resources (configured as needed)
```

---

## Prerequisites

### Required Software

```bash
# Terraform >= 1.0
terraform version

# AWS CLI
aws --version

# kubectl (Kubernetes CLI)
kubectl version --client

# Helm (Kubernetes package manager)
helm version
```

### AWS Credentials

Configure AWS credentials using one of these methods:

```bash
# Option 1: AWS CLI configuration
aws configure

# Option 2: Environment variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"

# Option 3: AWS credentials file (~/.aws/credentials)
[default]
aws_access_key_id = your-access-key
aws_secret_access_key = your-secret-key
```

### EKS Cluster

An existing EKS cluster must be available. Verify access:

```bash
# List available clusters
aws eks list-clusters --region us-east-1

# Get cluster details
aws eks describe-cluster --name your-cluster-name --region us-east-1

# Configure kubectl
aws eks update-kubeconfig --name your-cluster-name --region us-east-1

# Verify cluster access
kubectl cluster-info
```

---

## Quick Start

### 1. Initialize Terraform

```bash
cd terraform
terraform init
```

This command:
- Downloads required Terraform providers (aws, kubernetes, helm)
- Initializes the backend for state storage
- Creates `.terraform/` directory with provider plugins

### 2. Review Environment Configuration

Choose your environment and review the variables file:

```bash
# Available environments:
# - environments/dev.tfvars
# - environments/staging.tfvars
# - environments/production.tfvars

cat environments/dev.tfvars
```

### 3. Plan Deployment

```bash
# Generate an execution plan
terraform plan -var-file="environments/dev.tfvars"
```

Review the output to ensure the planned changes are correct.

### 4. Apply Configuration

```bash
# Deploy infrastructure
terraform apply -var-file="environments/dev.tfvars"
```

Confirm the deployment when prompted. Terraform will:
- Create/update AWS resources
- Configure Kubernetes providers
- Deploy Helm charts

### 5. Verify Deployment

```bash
# Check Helm releases
helm list -n default

# View deployed pods
kubectl get pods -n default

# Check service status
kubectl get svc -n default

# View Terraform outputs
terraform output
```

---

## Project Structure

```
terraform/
├── README.md                           # This file
├── main.tf                             # Main configuration: providers and helm_release
├── variables.tf                        # Input variables definition (AWS region, environment, cluster, etc.)
├── outputs.tf                          # Output values (cluster endpoint, namespace, etc.)
├── locals.tf                           # Local values for common configurations
├── terraform.tf                        # Terraform version and backend configuration
├── backend.tf                          # S3 backend configuration for state storage
├── .terraform.lock.hcl                 # Dependency lock file
│
├── environments/                       # Environment-specific variable files
│   ├── dev.tfvars                      # Development environment config
│   ├── staging.tfvars                  # Staging environment config
│   ├── production.tfvars               # Production environment config
│   ├── backend-dev.tfvars              # S3 backend config for dev
│   ├── backend-staging.tfvars          # S3 backend config for staging
│   └── backend-production.tfvars       # S3 backend config for production
│
├── modules/                            # Reusable Terraform modules
│   └── gke-deployment/                 # GKE deployment module (extensible for future use)
│
├── Documentation Files:
├── INDEX.md                            # Navigation guide for documentation
├── SETUP.md                            # Detailed setup instructions
├── CI_CD.md                            # CI/CD pipeline integration
├── TROUBLESHOOTING.md                  # Common issues and solutions
└── .gitignore                          # Git ignore patterns (excludes sensitive files)
```

### Key Files Explained

| File | Purpose |
|------|---------|
| **main.tf** | Defines AWS and Kubernetes providers, EKS cluster data sources, and Helm release resource for mainwebsite deployment |
| **variables.tf** | Declares all input variables (region, cluster_name, environment, helm settings, etc.) with validation rules |
| **outputs.tf** | Exports important values (cluster endpoint, namespace, Helm release status) for reference |
| **locals.tf** | Defines computed local values to keep configuration DRY |
| **terraform.tf** | Specifies Terraform version requirements and backend configuration |
| **backend.tf** | Configures S3 remote state storage with DynamoDB locking |

---

## Configuration

### Environment-Specific Variables

Edit the appropriate `.tfvars` file to customize your deployment:

```hcl
# environments/dev.tfvars
region               = "us-east-1"
environment          = "dev"
cluster_name         = "aws-info-website-dev"
kubernetes_namespace = "dev"
```

### Key Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `region` | Yes | `us-east-1` | AWS region for deployment |
| `environment` | Yes | N/A | Environment name: dev, staging, or production |
| `cluster_name` | Yes | N/A | Name of the existing EKS cluster |
| `kubernetes_namespace` | No | `default` | Kubernetes namespace for deployment |
| `helm_release_name` | No | `mainwebsite` | Helm release name |
| `helm_chart_path` | No | `../helm-dir` | Path to Helm chart directory |
| `helm_timeout` | No | `600` | Timeout for Helm operations (seconds) |
| `helm_atomic_deployment` | No | `false` | Rollback release if deployment fails |

For complete variable documentation, see [variables.tf](variables.tf).

---

## Deployment

### Development Environment

```bash
# Plan changes
terraform plan -var-file="environments/dev.tfvars"

# Apply changes
terraform apply -var-file="environments/dev.tfvars"

# Output values
terraform output -raw cluster_endpoint
```

### Staging Environment

```bash
terraform plan -var-file="environments/staging.tfvars"
terraform apply -var-file="environments/staging.tfvars"
```

### Production Environment

```bash
# Always plan before production deployments
terraform plan -var-file="environments/production.tfvars" > plan.out

# Review the plan file carefully
cat plan.out

# Apply with approval
terraform apply plan.out
```

### Common Operations

```bash
# Refresh state without changes
terraform refresh -var-file="environments/dev.tfvars"

# Destroy infrastructure (use with caution!)
terraform destroy -var-file="environments/dev.tfvars"

# Destroy specific resource
terraform destroy -var-file="environments/dev.tfvars" -target=helm_release.mainwebsite

# View current state
terraform show

# Validate configuration
terraform validate

# Format configuration files
terraform fmt -recursive
```

---

## Documentation

Comprehensive documentation is available:

| Document | Purpose |
|----------|---------|
| [INDEX.md](INDEX.md) | Navigation guide for all documentation |
| [SETUP.md](SETUP.md) | Detailed installation and setup instructions |
| [CI_CD.md](CI_CD.md) | CI/CD pipeline integration with Jenkins |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Solutions for common issues and debugging tips |

### For Different Roles

- **New Team Member**: Start with [SETUP.md](SETUP.md) and [Quick Start](#quick-start)
- **Terraform Developer**: Review [variables.tf](variables.tf) and [locals.tf](locals.tf)
- **DevOps Engineer**: Check [CI_CD.md](CI_CD.md) and [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## Troubleshooting

### Common Issues

**Issue: "Provider configuration not present" error**

Solution: Ensure all required variables are provided:
```bash
terraform apply -var-file="environments/dev.tfvars"
```

**Issue: EKS authentication fails**

Solution: Update kubeconfig and verify AWS credentials:
```bash
aws eks update-kubeconfig --name your-cluster-name --region us-east-1
aws sts get-caller-identity  # Verify AWS credentials
```

**Issue: Helm chart not found**

Solution: Verify the Helm chart path is correct:
```bash
ls -la ../helm-dir/
helm lint ../helm-dir/
```

**Issue: State lock timeout**

Solution: If Terraform is stuck, check for orphaned DynamoDB locks:
```bash
aws dynamodb scan --table-name terraform-locks --region us-east-1
```

### Getting Help

For detailed troubleshooting steps and advanced debugging, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

---

## Best Practices

- ✅ Always run `terraform plan` before applying changes
- ✅ Use environment-specific `.tfvars` files
- ✅ Keep `terraform.tfstate` and credentials secure (excluded in .gitignore)
- ✅ Review and commit `.terraform.lock.hcl` to version control
- ✅ Use Terraform workspaces for managing multiple environments
- ✅ Tag resources appropriately for cost tracking
- ✅ Implement automated backups for state files
- ✅ Document changes in commit messages

---

## Useful Commands

```bash
# Validation
terraform validate
terraform fmt -recursive

# Planning & Execution
terraform plan -var-file="environments/dev.tfvars" -out=plan.tfplan
terraform apply plan.tfplan

# State Management
terraform state list
terraform state show aws_eks_cluster.cluster
terraform state rm resource_type.resource_name

# Debugging
terraform console
terraform graph | dot -Tsvg > graph.svg
TF_LOG=DEBUG terraform apply -var-file="environments/dev.tfvars"

# Cleanup
terraform fmt .
terraform validate
```

---

## Related Resources

- **Project Root**: [../README.md](../README.md)
- **Helm Charts**: [../helm-dir/README.md](../helm-dir/README.md)
- **Main Application**: [../mainwebsite/README.md](../mainwebsite/README.md)
- **CI/CD Pipelines**: Jenkins configuration files (Jenkinsfile.*)

---

## Support

For issues, questions, or contributions:

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for known issues
2. Review [INDEX.md](INDEX.md) for documentation navigation
3. Consult the [LICENSE](../LICENSE) file for licensing information

---

**Last Updated**: January 2, 2026  
**Terraform Version**: >= 1.0  
**AWS Region**: Configurable (default: us-east-1)
