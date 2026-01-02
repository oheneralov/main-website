# Terraform Project - AWS Website Infrastructure

## 📋 Overview

This Terraform project manages the deployment of the AWS Info Website application on Amazon EKS (Elastic Kubernetes Service). It handles:
- AWS provider configuration and authentication
- Kubernetes and Helm provider setup
- Helm chart deployment to EKS cluster
- Multi-environment support (dev, staging, production)

## 🏗️ Project Structure

```
terraform/
├── terraform.tf              # Terraform version & provider requirements
├── main.tf                   # Main resources and provider configuration
├── variables.tf              # Input variables with validation
├── outputs.tf                # Output values
├── locals.tf                 # Local computed values
├── .gitignore               # Git ignore rules
│
├── environments/             # Environment-specific variables
│   ├── dev.tfvars           # Development environment
│   ├── staging.tfvars       # Staging environment
│   └── production.tfvars    # Production environment
│
├── modules/                  # Reusable Terraform modules
│   └── gke-deployment/      # GKE deployment module
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
│
└── docs/                     # Documentation
    ├── README.md            # This file
    ├── SETUP.md             # Setup instructions
    ├── BEST_PRACTICES.md    # Best practices guide
    └── TROUBLESHOOTING.md   # Troubleshooting guide
```

## 🚀 Quick Start

### Prerequisites
- Terraform >= 1.0
- AWS account with appropriate permissions
- EKS cluster already created
- AWS CLI configured with credentials
- kubectl configured for the EKS cluster
- Helm >= 3.0 installed

### 1. Initialize Terraform

```bash
cd terraform
terraform init
```

### 2. Plan Deployment

```bash
# Development
terraform plan -var-file="environments/dev.tfvars" -out=tfplan

# Staging
terraform plan -var-file="environments/staging.tfvars" -out=tfplan

# Production
terraform plan -var-file="environments/production.tfvars" -out=tfplan
```

### 3. Apply Configuration

```bash
# Apply the plan (use with caution in production)
terraform apply tfplan

# Or directly apply
terraform apply -var-file="environments/production.tfvars"
```

### 4. Verify Deployment

```bash
# Get deployment information
terraform output

# Check Helm release
helm list -n <namespace>

# Check pods
kubectl get pods -n <namespace>
```

## 🔧 Terraform Setup Guide

### Prerequisites Installation

#### Install Terraform
```bash
# macOS (using Homebrew)
brew tap hashicorp/tap
brew install hashicorp/tap/terraform

# Windows (using Chocolatey)
choco install terraform

# Linux
wget https://releases.hashicorp.com/terraform/1.5.0/terraform_1.5.0_linux_amd64.zip
unzip terraform_1.5.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/
```

#### Install Required Tools
```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### AWS Setup

#### 1. Configure AWS Credentials
```bash
# Option 1: Using AWS CLI
aws configure

# Option 2: Using environment variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"

# Verify credentials
aws sts get-caller-identity
```

#### 2. Verify AWS Permissions
```bash
# Ensure you have permissions for EKS and S3
aws iam list-user-policies --user-name $(aws iam get-user --query User.UserName --output text)

# Or check assumed role policies if using IAM role
aws sts get-assumed-role-user
```

#### 3. Configure EKS Access
```bash
# Update kubeconfig with EKS cluster credentials
aws eks update-kubeconfig --name <cluster-name> --region us-east-1

# Verify access
kubectl cluster-info
kubectl get nodes
```

### Initial Setup Steps

#### 1. Clone Repository and Navigate
```bash
git clone <repository-url>
cd aws-info-website/terraform
```

#### 2. Setup Environment Variables
Create a local environment configuration file:
```bash
# Create .env file (not committed to git)
cat > .env << EOF
export AWS_REGION="us-east-1"
export AWS_PROFILE="default"
export TF_VAR_region="us-east-1"
export TF_VAR_cluster_name="aws-info-website-dev"
export TF_VAR_environment="dev"
EOF

# Source the environment
source .env
```

#### 3. Update Environment Variables
```bash
# Edit environment-specific tfvars files
# Development
vi environments/dev.tfvars

# Staging
vi environments/staging.tfvars

# Production
vi environments/production.tfvars

# Update the following placeholders:
# - terraform_state_bucket: Replace "your-account-id" with your AWS account ID
# - cluster_name: Ensure it matches your EKS cluster name
# - region: Verify the AWS region matches your EKS cluster region
```

#### 4. Initialize Terraform Backend
```bash
# Option 1: Initialize with local state (for testing)
terraform init

# Option 2: Initialize with S3 backend (for production)
# First create S3 bucket
aws s3 mb s3://tf-state-dev-<your-account-id> --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket tf-state-dev-<your-account-id> \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket tf-state-dev-<your-account-id> \
  --server-side-encryption-configuration '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'

# Block public access
aws s3api put-public-access-block \
  --bucket tf-state-dev-<your-account-id> \
  --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# (Optional) Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# Initialize with backend config
terraform init -backend-config=environments/backend-dev.tfvars
```

#### 5. Validate Configuration
```bash
terraform validate
terraform fmt -recursive
tflint
```

#### 6. Plan and Apply
```bash
# Development
terraform plan -var-file="environments/dev.tfvars" -out=tfplan
terraform apply tfplan

# Check deployment
terraform output
kubectl get pods -n development
```

### Post-Setup Verification

```bash
# Verify Helm release
helm list -n development

# Check service endpoints
kubectl get svc -n development

# View deployment logs
kubectl logs -n development -l app=mainwebsite

# Test connectivity
kubectl port-forward -n development svc/mainwebsite 8080:3000
curl http://localhost:8080
```

## 🤖 Jenkins Integration Setup

### Jenkins Prerequisites

#### Required Jenkins Plugins
Install these plugins in Jenkins:
- Pipeline (Declarative Pipeline)
- GitHub or GitLab (depending on your VCS)
- Amazon Web Services (AWS) credentials plugin
- Docker Pipeline
- Terraform Plugin (or similar)
- Credentials Binding Plugin
- AWS S3 Plugin
- Slack Notification Plugin (optional)

#### Jenkins System Configuration

1. **Manage Jenkins → Manage Credentials**
   - Add AWS Access Key credentials (Access Key ID and Secret Access Key)
   - Credential ID: `aws-credentials`

2. **Manage Jenkins → Configure System**
   - AWS Credentials
   - Configure AWS region and credentials
   - Configure EKS cluster access

3. **Manage Jenkins → Configure Global Security**
   - Enable CSRF protection
   - Configure authentication method (LDAP, GitHub OAuth, etc.)

### Jenkins Pipeline Configuration

#### 1. Create Build Pipeline Job

Create a Jenkins pipeline job that uses `Jenkinsfile.build`:

```groovy
// Example pipeline configuration
pipeline {
    agent any
    
    triggers {
        githubPush()  // Trigger on GitHub push
    }
    
    environment {
        AWS_REGION = 'us-east-1'
        AWS_ACCOUNT_ID = credentials('aws-account-id')
        ECR_REGISTRY = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Validate Terraform') {
            steps {
                dir('terraform') {
                    sh '''
                        terraform init
                        terraform validate
                        terraform fmt -check -recursive
                    '''
                }
            }
        }
        
        // ... additional stages
    }
}
```

#### 2. Create Deploy Pipeline Job

Create a Jenkins pipeline job that uses `Jenkinsfile.deploy`:

**Job Configuration:**
- Select: Pipeline job
- Pipeline: Pipeline script from SCM
- SCM: Git
- Repository URL: Your Git repository
- Script Path: `Jenkinsfile.deploy`
- Parameters:
  - `DEPLOYMENT_ENV`: staging or production
  - `IMAGE_TAG`: Docker image tag

#### 3. Configure Credentials in Jenkins

Navigate to **Manage Jenkins → Manage Credentials → System → Global credentials**

Add the following credentials:

1. **AWS Access Key ID**
   - Type: Secret text
   - ID: `aws-access-key-id`
   - Secret: Your AWS Access Key ID

2. **AWS Secret Access Key**
   - Type: Secret text
   - ID: `aws-secret-access-key`
   - Secret: Your AWS Secret Access Key

3. **AWS Account ID**
   - Type: Secret text
   - ID: `aws-account-id`
   - Secret: Your AWS Account ID

4. **EKS Cluster Name**
   - Type: Secret text
   - ID: `eks-cluster-name`
   - Secret: Your EKS cluster name (e.g., `aws-info-website-dev`)

5. **ECR Registry URL**
   - Type: Secret text
   - ID: `ecr-registry-url`
   - Secret: `<account-id>.dkr.ecr.us-east-1.amazonaws.com`

### Jenkins Job Setup Steps

#### 1. Build Pipeline Job

```bash
# Job name: gcp-info-website-build
# Type: Pipeline
# Trigger: GitHub Push (webhook)

# Pipeline configuration:
# - Pipeline script from SCM
# - Git repository: <your-repo-url>
# - Script path: Jenkinsfile.build
```

**Build Job Stages:**
- Checkout
- Setup GCP Authentication
- Install Dependencies
- Lint Code
- Build Docker Images
- Push Images to GCR
- Run Tests
- Generate Reports

#### 2. Deploy Pipeline Job

```bash
# Job name: gcp-info-website-deploy
# Type: Parameterized Pipeline
# Trigger: Manual or after build success

# Parameters:
# - DEPLOYMENT_ENV (choice: staging, production)
# - IMAGE_TAG (string: default latest)
```

**Deploy Job Stages:**
- Checkout
- Setup GCP Authentication
- Verify Docker Images
- Configure kubectl
- Update Helm Values
- Deploy with Helm
- Verify Deployment
- Run Smoke Tests
- Notify Slack

#### 3. Validate Terraform Pipeline Job

```bash
# Job name: gcp-info-website-validate-terraform
# Type: Pipeline
# Trigger: Pull Request

# Pipeline stages:
# - Terraform Init
# - Terraform Validate
# - Terraform Format Check
# - TFLint
# - Security Scan (Optional)
```

### GitHub Webhook Setup (for automated builds)

1. Go to your GitHub repository
2. Settings → Webhooks → Add webhook
3. Payload URL: `http://<jenkins-url>/github-webhook/`
4. Content type: `application/json`
5. Events: Select "Push events"
6. Active: ✓ Check

### Jenkins Environment Configuration

#### Set Up Jenkins Build Node

```bash
# On Jenkins agent/node
# Install required tools
sudo apt-get update
sudo apt-get install -y \
    docker.io \
    terraform \
    kubectl \
    helm \
    git \
    npm \
    python3 \
    jq \
    awscli

# Configure Docker
sudo usermod -aG docker jenkins

# Configure AWS CLI
aws configure
```

#### Configure Jenkins Node Credentials

1. **Manage Jenkins → Manage Nodes**
2. **Agent node → Configure**
3. Add environment variables:
   ```
   DOCKER_HOST=unix:///var/run/docker.sock
   AWS_REGION=us-east-1
   AWS_DEFAULT_REGION=us-east-1
   KUBECONFIG=/var/lib/jenkins/.kube/config
   ```

### Monitoring and Notifications

#### Slack Notifications

1. Install Slack plugin
2. **Manage Jenkins → Configure System → Slack**
3. Add Slack workspace URL and token
4. In pipeline, add notification stage:

```groovy
post {
    success {
        slackSend(
            color: 'good',
            message: "Deployment Success: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
        )
    }
    failure {
        slackSend(
            color: 'danger',
            message: "Deployment Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
        )
    }
}
```

#### Email Notifications

1. **Manage Jenkins → Configure System → E-mail Notification**
2. Configure SMTP server details
3. In pipeline:

```groovy
post {
    always {
        emailext(
            to: 'team@example.com',
            subject: "Build ${env.BUILD_NUMBER}: ${currentBuild.result}",
            body: "Check console output at ${env.BUILD_URL}"
        )
    }
}
```

### CI/CD Workflow

```
GitHub Push
    ↓
Jenkins Build Trigger (Jenkinsfile.build)
    ├─ Checkout code
    ├─ Run tests
    ├─ Build Docker images
    └─ Push to GCR
    ↓
Manual Deployment Trigger (Jenkinsfile.deploy)
    ├─ Staging environment
    ├─ Run smoke tests
    ├─ Approve for production
    └─ Deploy to production
    ↓
Verify Deployment
    ├─ Health checks
    ├─ Helm verification
    └─ Slack notification
```

### Troubleshooting Jenkins Integration

**Issue**: Permission Denied when pulling images from ECR
```groovy
// Solution: Configure AWS credentials in Jenkins
withCredentials([string(credentialsId: 'aws-access-key-id', variable: 'AWS_ACCESS_KEY_ID'),
                string(credentialsId: 'aws-secret-access-key', variable: 'AWS_SECRET_ACCESS_KEY')]) {
    sh '''
        aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_REGISTRY
    '''
}
```

**Issue**: Terraform state lock conflicts
```bash
# Solution: Clear stuck locks
terraform force-unlock <LOCK_ID>

# Or use DynamoDB table for proper state locking
# Ensure dynamodb_table is configured in backend config
```

**Issue**: EKS authentication failures
```bash
# Solution: Update kubeconfig with IAM role
aws eks update-kubeconfig --name <cluster-name> --region us-east-1
kubectl auth can-i get pods --as-group system:masters
```

## 📝 Configuration Files

### terraform.tf
- **Purpose**: Terraform version and provider requirements
- **Contains**:
  - Required Terraform version (>= 1.0)
  - Provider version constraints
  - AWS provider configuration
  - S3 backend configuration for state management
  - Default tags for all resources

### variables.tf
- **Purpose**: Input variable definitions
- **Contains**:
  - AWS configuration (region)
  - Kubernetes configuration (cluster_name, namespace)
  - Helm configuration (chart path, release name, timeout)
  - Image tags for mainwebsite and metrics services
  - S3 state backend configuration
  - Validation rules for all inputs

### outputs.tf
- **Purpose**: Output values for reference
- **Contains**:
  - AWS and EKS cluster information
  - Helm release details
  - Environment information
  - Helpful kubectl/helm/AWS commands

### locals.tf
- **Purpose**: Local computed values
- **Contains**:
  - Resource naming conventions
  - Environment-specific configurations
  - Common labels
  - Helm file paths
  - Deployment metadata

### environments/*.tfvars
- **Purpose**: Environment-specific variable values
- **Files**:
  - `dev.tfvars` - Development configuration
  - `staging.tfvars` - Staging configuration
  - `production.tfvars` - Production configuration
- **Backend Files**:
  - `backend-dev.tfvars` - S3 backend config for dev
  - `backend-staging.tfvars` - S3 backend config for staging
  - `backend-production.tfvars` - S3 backend config for production

## 🔧 Variables

### Required Variables
- `region` - AWS region
- `cluster_name` - EKS cluster name
- `environment` - Environment type (dev, staging, production)

### Optional Variables with Defaults
- `kubernetes_namespace` (default: "default")
- `helm_chart_path` (default: "../helm-dir")
- `helm_release_name` (default: "mainwebsite")
- `helm_timeout` (default: 300 seconds)
- `helm_atomic_deployment` (default: true)
- `mainwebsite_image_tag` (default: "latest")
- `metrics_image_tag` (default: "latest")
- `terraform_state_bucket` - S3 bucket for Terraform state
- `terraform_state_key` (default: "aws-info-website/terraform")

### Variable Validation
All variables include validation rules:
- Format validation (regex patterns)
- Type checking
- Range validation for numeric values
- File existence checks (where applicable)

## 📊 Environment Differences

| Aspect | Dev | Staging | Production |
|--------|-----|---------|------------|
| Namespace | development | staging | production |
| Cluster | aws-info-website-dev | aws-info-website-staging | aws-info-website-prod |
| Mainwebsite Replicas | 1 | 2 | 3 |
| Metrics Replicas | 1 | 1 | 2 |
| Autoscaling | Disabled | Enabled (max 4) | Enabled (max 10) |
| Image Tags | dev-latest | staging-latest | 1.0.0 (explicit) |
| Monitoring | Disabled | Enabled | Enabled |
| Region | us-east-1 | us-east-1 | us-east-1 |
| State Backend | S3 with versioning | S3 with versioning | S3 with versioning + DynamoDB locks |

## 🔐 Security Best Practices

### Credentials Management
1. ✅ Store AWS credentials in `~/.aws/credentials` or environment variables
2. ✅ Use AWS IAM roles for EC2 instances and Lambda functions
3. ✅ Never commit AWS keys or credentials to version control
4. ✅ Rotate AWS access keys regularly
5. ✅ Use short-lived credentials when possible

### State Management
1. ✅ Use S3 backend for remote state (mandatory for team environments)
2. ✅ Enable S3 versioning on state buckets
3. ✅ Enable server-side encryption (AES256 or KMS)
4. ✅ Use DynamoDB table for state locking
5. ✅ Block public access to S3 state buckets
6. ✅ Enable S3 access logging

### Environment Isolation
1. ✅ Separate S3 buckets per environment (dev, staging, prod)
2. ✅ Different EKS clusters per environment
3. ✅ Different namespaces per environment
4. ✅ Distinct IAM roles/policies per environment
5. ✅ Use separate AWS accounts for production (recommended)

## 📋 Common Commands

### Plan Changes
```bash
terraform plan -var-file="environments/dev.tfvars"
terraform plan -var-file="environments/staging.tfvars" -out=tfplan
terraform plan -var-file="environments/production.tfvars"
```

### Apply Changes
```bash
terraform apply -var-file="environments/dev.tfvars"
terraform apply tfplan  # Apply saved plan
```

### View State
```bash
terraform state list
terraform state show helm_release.mainwebsite
terraform show
```

### Destroy Resources
```bash
# Development (safe to test)
terraform destroy -var-file="environments/dev.tfvars"

# Production (requires extra confirmation)
terraform destroy -var-file="environments/production.tfvars"
```

### Format & Validate
```bash
# Format HCL files
terraform fmt -recursive

# Validate configuration
terraform validate

# Validate with TFLint
tflint --init
tflint
```

## 🧪 Testing

### Validate Syntax
```bash
terraform validate
```

### Check Formatting
```bash
terraform fmt -check -recursive
```

### Lint with TFLint
```bash
tflint --init
tflint --format compact
```

### Dry Run (Plan)
```bash
terraform plan -var-file="environments/staging.tfvars" -out=tfplan.json
terraform show -json tfplan.json | jq
```

## 🐛 Troubleshooting

### Common Issues

**Issue**: "Error: InvalidAction. The action ListClusters is not valid for this web service"
```bash
# Solution: Verify AWS credentials and permissions
aws sts get-caller-identity
aws eks list-clusters

# Ensure you have EKS permissions
aws iam get-user-policy --user-name <your-username> --policy-name <policy-name>
```

**Issue**: "Error: resource type kubernetes_namespace not available"
```bash
# Solution: Ensure kubernetes provider is properly configured
terraform init -upgrade
```

**Issue**: "Error: helm_release error while running install action"
```bash
# Solution: Check Helm chart path and values
helm lint ../helm-dir/
helm template mainwebsite ../helm-dir/
```

**Issue**: "Error: error reading the TLS CA Certificate"
```bash
# Solution: Verify EKS cluster is accessible
aws eks describe-cluster --name <cluster-name> --region us-east-1
aws eks update-kubeconfig --name <cluster-name> --region us-east-1
kubectl cluster-info
```

**Issue**: "DynamoDB: User is not authorized to perform: dynamodb:DescribeTable"
```bash
# Solution: Ensure IAM user/role has DynamoDB permissions for state locking
# Either disable DynamoDB locking or grant permissions
```

### Debugging
```bash
# Enable debug logging
export TF_LOG=DEBUG
terraform apply -var-file="environments/dev.tfvars"
unset TF_LOG

# Check provider versions
terraform providers
terraform version

# Validate AWS access
aws s3 ls
aws eks list-clusters
```

## 📚 Additional Resources

### Documentation
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform Kubernetes Provider](https://registry.terraform.io/providers/hashicorp/kubernetes/latest/docs)
- [Terraform Helm Provider](https://registry.terraform.io/providers/hashicorp/helm/latest/docs)
- [AWS EKS Documentation](https://docs.aws.amazon.com/eks/)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [AWS DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)

### Best Practices
- See [BEST_PRACTICES.md](BEST_PRACTICES.md)
- See [SETUP.md](SETUP.md)

### Troubleshooting
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## 🤝 Contributing

When modifying this Terraform project:
1. Format code: `terraform fmt -recursive`
2. Validate syntax: `terraform validate`
3. Run linting: `tflint`
4. Test in dev first: `terraform plan -var-file="environments/dev.tfvars"`
5. Create descriptive commit messages

## 📞 Support

For issues or questions:
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review [BEST_PRACTICES.md](BEST_PRACTICES.md)
3. Check provider documentation
4. Review Terraform logs with `TF_LOG=DEBUG`

---

**Version**: 1.0  
**Last Updated**: January 2, 2026  
**Maintainer**: Platform Team
