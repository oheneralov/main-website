# Terraform CI/CD Integration Guide

This guide explains how to integrate Terraform deployments with CI/CD pipelines for automated, consistent infrastructure management.

---

## Overview

### Benefits of CI/CD for Terraform

- **Consistency**: Same deployment process every time
- **Automation**: Reduces manual errors and deployment time
- **Audit Trail**: Git history tracks all infrastructure changes
- **Review Process**: Pull request reviews before production changes
- **Environment Parity**: Identical deployment across dev/staging/prod
- **Rollback Safety**: Easy rollback to previous versions

---

## GitHub Actions Pipeline

### Prerequisites

1. GitHub repository with Terraform code
2. GCP service account with proper permissions
3. Secrets configured in GitHub repository

### Setup Secrets in GitHub

1. Go to repository Settings → Secrets and variables → Actions
2. Add the following secrets:

```
GCP_PROJECT_ID: clever-spirit-417020
GCP_CREDENTIALS: <service account JSON content>
```

### Basic Workflow: Validate & Plan

Create `.github/workflows/terraform-plan.yml`:

```yaml
name: Terraform Plan

on:
  pull_request:
    paths:
      - 'terraform/**'
      - '.github/workflows/terraform-plan.yml'

jobs:
  plan:
    runs-on: ubuntu-latest
    
    env:
      GOOGLE_APPLICATION_CREDENTIALS: ${{ runner.temp }}/gcp-key.json
      TF_VAR_credentials_file: ${{ runner.temp }}/gcp-key.json
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up GCP credentials
        run: |
          mkdir -p $(dirname $GOOGLE_APPLICATION_CREDENTIALS)
          echo '${{ secrets.GCP_CREDENTIALS }}' > $GOOGLE_APPLICATION_CREDENTIALS
          chmod 600 $GOOGLE_APPLICATION_CREDENTIALS
      
      - name: Set up Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.5.0
      
      - name: Terraform Format Check
        run: |
          cd terraform
          terraform fmt -check -recursive
      
      - name: Terraform Init
        run: |
          cd terraform
          terraform init
      
      - name: Terraform Validate
        run: |
          cd terraform
          terraform validate
      
      - name: Terraform Plan (Dev)
        run: |
          cd terraform
          terraform plan -var-file="environments/dev.tfvars" -out=tfplan-dev
      
      - name: Comment Plan on PR
        if: always()
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const plan = fs.readFileSync('terraform/tfplan-dev.txt', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '## Terraform Plan\n```\n' + plan + '\n```'
            });
```

### Deployment Workflow: Apply

Create `.github/workflows/terraform-apply.yml`:

```yaml
name: Terraform Apply

on:
  push:
    branches:
      - main
    paths:
      - 'terraform/**'

jobs:
  plan:
    runs-on: ubuntu-latest
    outputs:
      plan_exists: ${{ steps.plan.outputs.exists }}
    
    env:
      GOOGLE_APPLICATION_CREDENTIALS: ${{ runner.temp }}/gcp-key.json
      TF_VAR_credentials_file: ${{ runner.temp }}/gcp-key.json
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up GCP credentials
        run: |
          mkdir -p $(dirname $GOOGLE_APPLICATION_CREDENTIALS)
          echo '${{ secrets.GCP_CREDENTIALS }}' > $GOOGLE_APPLICATION_CREDENTIALS
      
      - name: Set up Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.5.0
      
      - name: Terraform Init
        run: |
          cd terraform
          terraform init
      
      - name: Terraform Plan
        id: plan
        run: |
          cd terraform
          terraform plan -var-file="environments/dev.tfvars" -out=tfplan
          echo "exists=true" >> $GITHUB_OUTPUT
  
  apply:
    needs: plan
    runs-on: ubuntu-latest
    if: needs.plan.outputs.plan_exists == 'true'
    
    env:
      GOOGLE_APPLICATION_CREDENTIALS: ${{ runner.temp }}/gcp-key.json
      TF_VAR_credentials_file: ${{ runner.temp }}/gcp-key.json
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up GCP credentials
        run: |
          mkdir -p $(dirname $GOOGLE_APPLICATION_CREDENTIALS)
          echo '${{ secrets.GCP_CREDENTIALS }}' > $GOOGLE_APPLICATION_CREDENTIALS
      
      - name: Set up Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.5.0
      
      - name: Terraform Init
        run: |
          cd terraform
          terraform init
      
      - name: Terraform Apply
        run: |
          cd terraform
          terraform apply -auto-approve tfplan
      
      - name: Get Outputs
        id: outputs
        run: |
          cd terraform
          echo "cluster_endpoint=$(terraform output -raw gke_cluster_endpoint)" >> $GITHUB_OUTPUT
      
      - name: Notify Deployment
        run: |
          echo "Deployment completed to ${{ steps.outputs.outputs.cluster_endpoint }}"
```

---

## Google Cloud Build Pipeline

### Prerequisites

1. Cloud Build enabled in GCP
2. Service account with Terraform permissions
3. Terraform code in Cloud Source Repositories or GitHub

### Create cloudbuild.yaml

```yaml
steps:
  # Step 1: Validate Terraform
  - name: 'gcr.io/cloud-builders/terraform'
    id: 'validate'
    args:
      - 'validate'
      - '-no-color'
    dir: 'terraform'
    env:
      - 'CLOUDSDK_COMPUTE_REGION=us-central1'

  # Step 2: Format Check
  - name: 'gcr.io/cloud-builders/terraform'
    id: 'fmt-check'
    args:
      - 'fmt'
      - '-check'
      - '-recursive'
      - '-no-color'
    dir: 'terraform'

  # Step 3: Plan (Dev)
  - name: 'gcr.io/cloud-builders/terraform'
    id: 'plan-dev'
    args:
      - 'plan'
      - '-var-file=environments/dev.tfvars'
      - '-out=tfplan-dev'
      - '-no-color'
    dir: 'terraform'
    env:
      - 'CLOUDSDK_COMPUTE_REGION=us-central1'

  # Step 4: Apply (only on main branch)
  - name: 'gcr.io/cloud-builders/terraform'
    id: 'apply-dev'
    args:
      - 'apply'
      - '-no-color'
      - '-auto-approve'
      - 'tfplan-dev'
    dir: 'terraform'
    onFailure:
      - 'ALLOW'
    env:
      - 'CLOUDSDK_COMPUTE_REGION=us-central1'

  # Step 5: Get outputs
  - name: 'gcr.io/cloud-builders/terraform'
    id: 'outputs'
    args:
      - 'output'
      - '-no-color'
    dir: 'terraform'

# Only run on main branch for apply
onPush:
  branch:
    - main
```

### Deploy with Cloud Build

```bash
# Manual trigger
gcloud builds submit --config cloudbuild.yaml

# View build logs
gcloud builds log <BUILD_ID>

# Monitor builds
gcloud builds list --limit 10
```

---

## GitLab CI Pipeline

### Create .gitlab-ci.yml

```yaml
stages:
  - validate
  - plan
  - apply

variables:
  TF_VERSION: "1.5.0"
  TF_DIR: "terraform"
  TF_ROOT: "${CI_PROJECT_DIR}/${TF_DIR}"

before_script:
  - apt-get update && apt-get install -y curl unzip
  - curl -sL "https://releases.hashicorp.com/terraform/${TF_VERSION}/terraform_${TF_VERSION}_linux_amd64.zip" -o terraform.zip
  - unzip terraform.zip
  - rm terraform.zip
  - export PATH=$PWD:$PATH
  - cd ${TF_ROOT}

validate:
  stage: validate
  script:
    - terraform version
    - terraform fmt -check -recursive
    - terraform init
    - terraform validate

plan_dev:
  stage: plan
  script:
    - terraform init
    - terraform plan -var-file="environments/dev.tfvars" -out=tfplan
  artifacts:
    paths:
      - ${TF_DIR}/tfplan
    expire_in: 1 hour
  only:
    - merge_requests
    - main

apply_dev:
  stage: apply
  script:
    - terraform init
    - terraform apply -auto-approve tfplan
  dependencies:
    - plan_dev
  only:
    - main
  when: manual
```

---

## Best Practices for CI/CD

### 1. Separate Pipelines by Environment

```yaml
# Plan PRs for dev/staging
# Apply main for dev
# Manual approval for staging/prod
```

### 2. Security

```yaml
# Use OIDC for GCP authentication (no static credentials)
# Mask sensitive outputs
# Audit all changes
# Require PR reviews
```

### 3. Workflow

```yaml
- Feature branch: terraform fmt, validate, plan
- Pull request: Show plan, require review
- Merge to main: Auto-apply to dev
- Manual promotion: Staging/prod
```

### 4. Approval Process

```yaml
steps:
  - name: Request Manual Approval
    if: github.ref == 'refs/heads/main'
    uses: trstringer/manual-approval@v1
    with:
      secret: ${{ secrets.GITHUB_TOKEN }}
      approvers: platform-team
      issue-title: 'Approve terraform apply to production'
```

### 5. Notifications

```yaml
# Slack notifications
- name: Notify Slack
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "Terraform deployment completed",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "Cluster: ${{ steps.outputs.outputs.cluster_endpoint }}"
            }
          }
        ]
      }
```

---

## Multi-Environment Strategy

### Development (Auto-Apply)

```yaml
plan_dev:
  only:
    - merge_requests

apply_dev:
  only:
    - main
  script:
    - terraform apply -auto-approve tfplan-dev
```

### Staging (Manual Approval)

```yaml
apply_staging:
  only:
    - main
  when: manual
  script:
    - terraform apply -auto-approve tfplan-staging
```

### Production (Protected + Multiple Approvals)

```yaml
apply_prod:
  only:
    - main
  when: manual
  script:
    - terraform apply -auto-approve tfplan-prod
  environment:
    name: production
    url: ${{ secrets.PROD_CLUSTER_URL }}
  allow_failure: false
```

---

## State Management in CI/CD

### Remote State (Recommended)

```hcl
# terraform/terraform.tf
terraform {
  backend "gcs" {
    bucket  = "your-project-terraform-state"
    prefix  = "gcp-info-website"
  }
}
```

### State Locking

```bash
# Automatically handled by remote backend
# Prevents concurrent modifications
```

### State Backup

```bash
# Enable GCS versioning
gsutil versioning set on gs://your-project-terraform-state

# Keep versions
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
```

---

## Monitoring & Alerts

### Deployment Notifications

```yaml
- name: Send deployment summary
  run: |
    echo "=== Deployment Summary ===" >> $GITHUB_STEP_SUMMARY
    echo "Environment: dev" >> $GITHUB_STEP_SUMMARY
    echo "Cluster: ${{ steps.outputs.outputs.cluster_endpoint }}" >> $GITHUB_STEP_SUMMARY
    echo "Status: Success" >> $GITHUB_STEP_SUMMARY
```

### Health Checks

```bash
# Post-deployment validation
- name: Health Check
  run: |
    kubectl get nodes -n production
    kubectl get pods -n production
    kubectl get svc -n production
```

### Rollback Strategy

```yaml
- name: Rollback on Failure
  if: failure()
  run: |
    # Get previous state version
    terraform state pull > previous-state.json
    # Apply previous state
    terraform apply -var-file="environments/dev.tfvars" -auto-approve
    # Notify team
    echo "Rollback triggered"
```

---

## Examples & Templates

### Quick Start: GitHub Actions

1. Copy `.github/workflows/terraform-plan.yml` to repository
2. Configure secrets: `GCP_PROJECT_ID`, `GCP_CREDENTIALS`
3. Create pull request
4. GitHub Actions will automatically plan the changes

### Quick Start: Cloud Build

1. Copy `cloudbuild.yaml` to repository
2. Set up Cloud Build trigger
3. Push to main branch
4. Cloud Build will automatically apply changes

### Quick Start: GitLab CI

1. Copy `.gitlab-ci.yml` to repository
2. Set up CI/CD variables in GitLab
3. Create merge request
4. Pipeline will automatically validate and plan

---

## Troubleshooting CI/CD

### Issue: "Error acquiring the state lock"

**Solution**: 
```bash
# Check lock
gsutil ls -L gs://bucket/terraform.tfstate

# Force unlock (use carefully)
terraform force-unlock <LOCK_ID>
```

### Issue: "Authentication failed"

**Solution**:
```bash
# Verify credentials in secrets
# Ensure service account has required roles
gcloud projects get-iam-policy $PROJECT_ID
```

### Issue: "Deployment timeout"

**Solution**:
```yaml
# Increase timeout in CI/CD config
env:
  TF_TIMEOUT: "600s"
  HELM_TIMEOUT: "600s"
```

---

## Security Considerations

1. **Never commit credentials** - Use secrets/environment variables
2. **Audit all changes** - Git history tracks infrastructure changes
3. **Review before production** - PR review required for prod changes
4. **Use OIDC authentication** - Better than static credentials
5. **Rotate credentials regularly** - Service account keys
6. **Least privilege** - Minimal required IAM permissions
7. **Separate state by environment** - Dev/staging/prod isolation
8. **Encrypted state** - Enable encryption at rest
9. **Audit logging** - Track who changed what
10. **Backup state regularly** - Regular snapshots

---

## Additional Resources

- [Terraform Cloud/Enterprise](https://www.terraform.io/cloud)
- [GitHub Actions Best Practices](https://docs.github.com/en/actions)
- [Google Cloud Build Documentation](https://cloud.google.com/docs/ci-cd)
- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)

---

**Last Updated**: January 2, 2026
