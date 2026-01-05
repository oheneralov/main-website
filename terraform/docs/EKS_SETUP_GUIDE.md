# EKS Cluster Setup and Management Guide

This guide covers creating and managing an AWS EKS (Elastic Kubernetes Service) cluster using Terraform, along with deploying your applications via Helm.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Configuration](#configuration)
4. [Deployment](#deployment)
5. [Verification](#verification)
6. [Common Operations](#common-operations)
7. [Troubleshooting](#troubleshooting)
8. [Cleanup](#cleanup)

## Prerequisites

### Required Tools
- **Terraform** >= 1.0
- **AWS CLI** >= 2.0
- **kubectl** >= 1.28
- **Helm** >= 3.0
- **aws-iam-authenticator** (for kubectl authentication)

### AWS Permissions
Your AWS credentials need the following permissions:
- EKS cluster creation and management
- VPC and subnet management
- IAM role creation
- CloudWatch Logs (for cluster logging)
- EC2 instance management (for node groups)

### Network Prerequisites
- A VPC with at least 2 subnets (recommended 3+ for HA)
- Subnets should be in different availability zones
- Subnets must have the following tags:
  - `kubernetes.io/cluster/{cluster-name}` = `shared`
  - `kubernetes.io/role/elb` = `1` (for public subnets)
  - `kubernetes.io/role/internal-elb` = `1` (for private subnets)

## Quick Start

### 1. Prepare Your Configuration

Copy the example tfvars file:
```bash
cd terraform
cp environments/example-dev.tfvars environments/dev.tfvars
```

### 2. Update Subnet IDs

Edit `environments/dev.tfvars` and replace subnet IDs:
```hcl
subnet_ids = [
  "subnet-12345678",  # Your private subnet 1
  "subnet-87654321"   # Your private subnet 2
]
```

Get your subnet IDs:
```bash
aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=vpc-xxxxx" \
  --query 'Subnets[].{ID:SubnetId,AZ:AvailabilityZone,CIDR:CidrBlock}' \
  --output table
```

### 3. Initialize Terraform

```bash
terraform init
```

### 4. Plan the Deployment

```bash
terraform plan -var-file="environments/dev.tfvars"
```

### 5. Apply the Configuration

```bash
terraform apply -var-file="environments/dev.tfvars"
```

## Configuration

### Key Variables

#### Cluster Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `create_cluster` | `true` | Create new cluster or reference existing |
| `cluster_name` | N/A | Name of the EKS cluster |
| `kubernetes_version` | `1.28` | Kubernetes version to use |
| `subnet_ids` | N/A | VPC subnet IDs for cluster |
| `cluster_endpoint_public_access` | `true` | Allow public access to API |

#### Node Group Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `node_group_min_size` | `2` | Minimum nodes in cluster |
| `node_group_max_size` | `10` | Maximum nodes in cluster |
| `node_group_desired_size` | `3` | Initial number of nodes |
| `node_instance_types` | `["t3.medium"]` | EC2 instance types for nodes |
| `node_disk_size` | `50` | Root disk size in GB |

#### Environment-Specific Overrides

**Development** (`environments/dev.tfvars`):
```hcl
node_group_desired_size = 2
node_instance_types = ["t3.medium"]
```

**Staging** (`environments/staging.tfvars`):
```hcl
node_group_desired_size = 3
node_instance_types = ["t3.medium"]
```

**Production** (`environments/production.tfvars`):
```hcl
node_group_desired_size = 5
node_instance_types = ["t3.large", "t3a.large"]
```

### Customizing Helm Deployment

Edit helm values in the tfvars files:

```hcl
helm_set_values = {
  "mainwebsite.replicaCount"        = "3"
  "mainwebsite.autoscaling.enabled" = "true"
  "mainwebsite.autoscaling.maxReplicas" = "10"
  "metrics.replicaCount"            = "2"
}
```

## Deployment

### Deploy to Development

```bash
cd terraform
terraform apply -var-file="environments/dev.tfvars"
```

### Deploy to Staging

```bash
terraform apply -var-file="environments/staging.tfvars"
```

### Deploy to Production

```bash
terraform apply -var-file="environments/production.tfvars"
```

### Update Only the Kubernetes Application (without recreating cluster)

```bash
# Plan the changes
terraform plan \
  -var-file="environments/prod.tfvars" \
  -target=helm_release.mainwebsite

# Apply just the Helm release
terraform apply \
  -var-file="environments/prod.tfvars" \
  -target=helm_release.mainwebsite
```

## Verification

### Get Cluster Information

```bash
# Get all outputs
terraform output

# Get specific cluster info
terraform output eks_cluster_endpoint
terraform output eks_cluster_arn
```

### Configure kubectl

```bash
# Configure kubeconfig
aws eks update-kubeconfig \
  --region us-east-1 \
  --name aws-info-website-dev

# Verify connection
kubectl cluster-info
kubectl get nodes
```

### Check Deployed Applications

```bash
# List all Helm releases
helm list -A

# Get Helm release status
helm status mainwebsite -n development

# View deployed resources
kubectl get all -n development
kubectl get pods -n development
kubectl logs -n development -l app=mainwebsite
```

### Monitor Cluster

```bash
# Check cluster health
kubectl get cs

# View cluster events
kubectl get events

# Monitor node status
kubectl get nodes -o wide
kubectl top nodes
kubectl top pods -n development
```

## Common Operations

### Scale Node Group

```bash
# Edit the tfvars file:
# node_group_desired_size = 5

# Apply changes
terraform apply -var-file="environments/prod.tfvars"
```

### Update Kubernetes Version

```bash
# 1. Update in tfvars
# kubernetes_version = "1.29"

# 2. Plan and review
terraform plan -var-file="environments/prod.tfvars"

# 3. Apply upgrade
terraform apply -var-file="environments/prod.tfvars"
```

### Update Application Deployment

```bash
# Update image tags in tfvars
# mainwebsite_image_tag = "1.2.0"
# metrics_image_tag = "1.1.0"

# Reapply only Helm charts
terraform apply \
  -var-file="environments/prod.tfvars" \
  -target=helm_release.mainwebsite
```

### Enable Additional Cluster Logging

```hcl
cluster_log_types = [
  "api",
  "audit", 
  "authenticator",
  "controllerManager",
  "scheduler"
]
```

### Restrict Public API Access

```hcl
# Change in tfvars
cluster_endpoint_public_access = false

# Or restrict to specific CIDR
cluster_endpoint_public_access_cidrs = [
  "203.0.113.0/24"  # Your company IP range
]
```

### Add Custom Security Group

```hcl
cluster_security_group_ids = [
  "sg-12345678"  # Your security group
]
```

## Troubleshooting

### Cluster Creation Fails

Check AWS CloudTrail logs:
```bash
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=aws-info-website-dev
```

### Nodes Not Ready

```bash
# Check node status
kubectl describe node <node-name>

# Check kubelet logs (SSH to node first)
journalctl -u kubelet -f

# Check cluster security group
aws ec2 describe-security-groups --group-ids sg-xxxxx
```

### Helm Release Deployment Failed

```bash
# Check Helm release status
helm status mainwebsite -n development

# Get release events
helm get all mainwebsite -n development

# Check pod logs
kubectl logs -n development -l release=mainwebsite --tail=50
```

### kubectl Context Issues

```bash
# Verify kubeconfig
kubectl config get-contexts

# Switch context
kubectl config use-context arn:aws:eks:us-east-1:ACCOUNT:cluster/aws-info-website-dev

# Recreate kubeconfig
aws eks update-kubeconfig \
  --region us-east-1 \
  --name aws-info-website-dev \
  --kubeconfig ~/.kube/config
```

### IAM Permission Denied

```bash
# Check IAM role trust relationship
aws iam get-role --role-name aws-info-website-dev-cluster-role

# Add your IAM user to aws-auth ConfigMap
kubectl edit configmap aws-auth -n kube-system
```

## Cleanup

### Destroy Specific Environment

```bash
terraform destroy -var-file="environments/dev.tfvars"
```

### Destroy All Resources

```bash
# Destroy all environments
terraform destroy -var-file="environments/dev.tfvars"
terraform destroy -var-file="environments/staging.tfvars"
terraform destroy -var-file="environments/production.tfvars"
```

### Manual Cleanup (if needed)

```bash
# Delete any manually created resources
# Remove load balancers, volumes, etc. that were created by applications

# Check what will be deleted first
terraform plan -destroy -var-file="environments/prod.tfvars"

# Then destroy
terraform destroy -var-file="environments/prod.tfvars"
```

## State Management

### Remote State with S3

To store Terraform state in S3 (recommended for team environments):

1. Create S3 bucket:
```bash
aws s3api create-bucket \
  --bucket terraform-state-aws-info-website \
  --region us-east-1

aws s3api put-bucket-versioning \
  --bucket terraform-state-aws-info-website \
  --versioning-configuration Status=Enabled

aws s3api put-bucket-encryption \
  --bucket terraform-state-aws-info-website \
  --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
```

2. Create `backend.tf`:
```hcl
terraform {
  backend "s3" {
    bucket         = "terraform-state-aws-info-website"
    key            = "aws-info-website/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}
```

3. Initialize backend:
```bash
terraform init
```

## Best Practices

1. **Version Control**: Store tfvars files securely (use .gitignore for sensitive data)
2. **State Locking**: Use S3 with DynamoDB for state locking
3. **Tagging**: Always use meaningful tags for cost tracking
4. **Backup**: Regular backups of etcd (handled by AWS for EKS)
5. **Monitoring**: Enable CloudWatch Container Insights
6. **Updates**: Plan for regular Kubernetes version updates
7. **Security**: Restrict cluster endpoint access in production
8. **Multi-AZ**: Always deploy across multiple availability zones

## Additional Resources

- [AWS EKS Documentation](https://docs.aws.amazon.com/eks/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Chart Best Practices](https://helm.sh/docs/chart_best_practices/)

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review AWS EKS CloudWatch logs
3. Check Terraform state: `terraform show`
4. Review Kubernetes events: `kubectl get events -A`
