################################################################################
# Terraform State Backend Configuration (Google Cloud Storage)
################################################################################
# This file configures Terraform to store its state in Google Cloud Storage (GCS)
# instead of locally. This enables:
# - Team collaboration (shared state)
# - Remote state locking (prevents concurrent modifications)
# - Better security (state stored in GCS with encryption)
# - CI/CD pipeline integration
#
# SETUP INSTRUCTIONS:
# ===================
#
# 1. Create GCS buckets for each environment:
#    gsutil mb -p YOUR_PROJECT_ID gs://tf-state-dev-YOUR_PROJECT_ID
#    gsutil mb -p YOUR_PROJECT_ID gs://tf-state-staging-YOUR_PROJECT_ID
#    gsutil mb -p YOUR_PROJECT_ID gs://tf-state-prod-YOUR_PROJECT_ID
#
# 2. Enable versioning on buckets (recommended):
#    gsutil versioning set on gs://tf-state-dev-YOUR_PROJECT_ID
#    gsutil versioning set on gs://tf-state-staging-YOUR_PROJECT_ID
#    gsutil versioning set on gs://tf-state-prod-YOUR_PROJECT_ID
#
# 3. Enable encryption on buckets (recommended):
#    gsutil encryption set gs://tf-state-dev-YOUR_PROJECT_ID
#    gsutil encryption set gs://tf-state-staging-YOUR_PROJECT_ID
#    gsutil encryption set gs://tf-state-prod-YOUR_PROJECT_ID
#
# 4. Restrict bucket access:
#    gsutil iam ch serviceAccount:YOUR_SA_EMAIL:objectAdmin gs://tf-state-dev-YOUR_PROJECT_ID
#    gsutil iam ch serviceAccount:YOUR_SA_EMAIL:objectAdmin gs://tf-state-staging-YOUR_PROJECT_ID
#    gsutil iam ch serviceAccount:YOUR_SA_EMAIL:objectAdmin gs://tf-state-prod-YOUR_PROJECT_ID
#
# 5. Initialize Terraform with GCS backend for each environment:
#
#    # For Development:
#    terraform init -backend-config=environments/backend-dev.tfvars
#
#    # For Staging:
#    terraform init -backend-config=environments/backend-staging.tfvars
#
#    # For Production:
#    terraform init -backend-config=environments/backend-production.tfvars
#
# 6. After initialization, you can use standard Terraform commands:
#    terraform plan -var-file=environments/dev.tfvars
#    terraform apply -var-file=environments/dev.tfvars
#
# MIGRATION FROM LOCAL STATE:
# ============================
#
# If you have existing local state files (terraform.tfstate), migrate them:
#
#    1. Initialize backend: terraform init -backend-config=environments/backend-dev.tfvars
#    2. Confirm migration when prompted
#    3. Verify state was uploaded: gsutil ls gs://tf-state-dev-YOUR_PROJECT_ID/
#    4. Keep local terraform.tfstate as backup
#    5. Add terraform.tfstate* to .gitignore if not already done
#
################################################################################
# Terraform State Backend Configuration (Amazon S3)
################################################################################
# This file configures Terraform to store its state in Amazon S3
# instead of locally. This enables:
# - Team collaboration (shared state)
# - Remote state locking (via DynamoDB)
# - Better security (state stored in S3 with encryption)
# - CI/CD pipeline integration
#
# SETUP INSTRUCTIONS:
# ===================
#
# 1. Create S3 buckets for each environment:
#    aws s3 mb s3://tf-state-dev-<your-account-id> --region us-east-1
#    aws s3 mb s3://tf-state-staging-<your-account-id> --region us-east-1
#    aws s3 mb s3://tf-state-prod-<your-account-id> --region us-east-1
#
# 2. Enable versioning on buckets (recommended):
#    aws s3api put-bucket-versioning --bucket tf-state-dev-<your-account-id> --versioning-configuration Status=Enabled
#    aws s3api put-bucket-versioning --bucket tf-state-staging-<your-account-id> --versioning-configuration Status=Enabled
#    aws s3api put-bucket-versioning --bucket tf-state-prod-<your-account-id> --versioning-configuration Status=Enabled
#
# 3. Enable encryption on buckets (recommended):
#    aws s3api put-bucket-encryption --bucket tf-state-dev-<your-account-id> --server-side-encryption-configuration '{\"Rules\": [{\"ApplyServerSideEncryptionByDefault\": {\"SSEAlgorithm\": \"AES256\"}}]}'
#    aws s3api put-bucket-encryption --bucket tf-state-staging-<your-account-id> --server-side-encryption-configuration '{\"Rules\": [{\"ApplyServerSideEncryptionByDefault\": {\"SSEAlgorithm\": \"AES256\"}}]}'
#    aws s3api put-bucket-encryption --bucket tf-state-prod-<your-account-id> --server-side-encryption-configuration '{\"Rules\": [{\"ApplyServerSideEncryptionByDefault\": {\"SSEAlgorithm\": \"AES256\"}}]}'
#
# 4. Block public access to buckets:
#    aws s3api put-public-access-block --bucket tf-state-dev-<your-account-id> --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
#    aws s3api put-public-access-block --bucket tf-state-staging-<your-account-id> --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
#    aws s3api put-public-access-block --bucket tf-state-prod-<your-account-id> --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
#
# 5. (Optional) Create DynamoDB table for state locking:
#    aws dynamodb create-table --table-name terraform-locks --attribute-definitions AttributeName=LockID,AttributeType=S --key-schema AttributeName=LockID,KeyType=HASH --billing-mode PAY_PER_REQUEST --region us-east-1
#
# 6. Initialize Terraform with S3 backend for each environment:
#
#    # For Development:
#    terraform init -backend-config=environments/backend-dev.tfvars
#
#    # For Staging:
#    terraform init -backend-config=environments/backend-staging.tfvars
#
#    # For Production:
#    terraform init -backend-config=environments/backend-production.tfvars
#
# 7. After initialization, you can use standard Terraform commands:
#    terraform plan -var-file=environments/dev.tfvars
#    terraform apply -var-file=environments/dev.tfvars
#
# MIGRATION FROM LOCAL STATE:
# ============================
#
# If you have existing local state files (terraform.tfstate), migrate them:
#
#    1. Initialize backend: terraform init -backend-config=environments/backend-dev.tfvars
#    2. Confirm migration when prompted
#    3. Verify state was uploaded: aws s3 ls s3://tf-state-dev-<your-account-id>/
#    4. Keep local terraform.tfstate as backup
#    5. Add terraform.tfstate* to .gitignore if not already done
#
# SECURITY BEST PRACTICES:
# =========================
# - Enable versioning on all state buckets
# - Enable MFA Delete protection
# - Enable bucket logging to track state access
# - Restrict IAM permissions to only necessary roles/users
# - Enable server-side encryption (AES256 or KMS)
# - Enable DynamoDB state locking with encryption
# - Regularly audit state file access via S3 access logs
# - Never commit state files to version control

