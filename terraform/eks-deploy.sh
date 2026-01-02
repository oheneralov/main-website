#!/bin/bash

################################################################################
# EKS Cluster Deployment Helper Script
# Usage: ./eks-deploy.sh [dev|staging|prod] [plan|apply|destroy]
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="${SCRIPT_DIR}"
ENVIRONMENTS=("dev" "staging" "production")
ACTIONS=("plan" "apply" "destroy" "output" "refresh")

################################################################################
# Functions
################################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_usage() {
    cat << EOF
Usage: $0 [ENVIRONMENT] [ACTION] [OPTIONS]

ENVIRONMENT:
    dev         - Development cluster
    staging     - Staging cluster
    prod        - Production cluster

ACTION:
    plan        - Show what will be created/changed
    apply       - Create/update cluster and applications
    destroy     - Delete cluster and all resources
    output      - Show cluster outputs
    refresh     - Refresh state without modifying infrastructure

OPTIONS:
    -h, --help          Show this help message
    -v, --var KEY=VAL   Override variables (can be used multiple times)
    --no-confirm        Skip confirmation prompts
    --target RESOURCE   Target specific resource

EXAMPLES:
    # Plan deployment to dev
    $0 dev plan

    # Apply to staging
    $0 staging apply

    # Destroy production (with confirmation)
    $0 prod destroy

    # Plan with variable override
    $0 dev plan -v node_group_desired_size=5

    # Target specific resource
    $0 dev apply --target aws_eks_node_group.main

EOF
    exit 0
}

validate_environment() {
    local env=$1
    if [[ ! " ${ENVIRONMENTS[@]} " =~ " ${env} " ]]; then
        log_error "Invalid environment: $env"
        echo "Valid environments: ${ENVIRONMENTS[@]}"
        exit 1
    fi
}

validate_action() {
    local action=$1
    if [[ ! " ${ACTIONS[@]} " =~ " ${action} " ]]; then
        log_error "Invalid action: $action"
        echo "Valid actions: ${ACTIONS[@]}"
        exit 1
    fi
}

get_tfvars_file() {
    local env=$1
    echo "${TERRAFORM_DIR}/environments/${env}.tfvars"
}

check_tfvars_exists() {
    local tfvars=$1
    if [ ! -f "$tfvars" ]; then
        log_error "tfvars file not found: $tfvars"
        exit 1
    fi
}

check_prerequisites() {
    local missing_tools=()
    
    # Check for required tools
    command -v terraform &> /dev/null || missing_tools+=("terraform")
    command -v aws &> /dev/null || missing_tools+=("aws")
    command -v kubectl &> /dev/null || missing_tools+=("kubectl")
    command -v helm &> /dev/null || missing_tools+=("helm")
    
    if [ ${#missing_tools[@]} -gt 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured"
        exit 1
    fi
    
    log_success "All prerequisites met"
}

terraform_init() {
    log_info "Initializing Terraform..."
    cd "$TERRAFORM_DIR"
    terraform init
    cd - > /dev/null
}

terraform_plan() {
    local environment=$1
    shift
    local extra_args=("$@")
    
    local tfvars=$(get_tfvars_file "$environment")
    check_tfvars_exists "$tfvars"
    
    log_info "Planning infrastructure for $environment..."
    cd "$TERRAFORM_DIR"
    terraform plan -var-file="$tfvars" "${extra_args[@]}"
    cd - > /dev/null
}

terraform_apply() {
    local environment=$1
    shift
    local extra_args=("$@")
    
    local tfvars=$(get_tfvars_file "$environment")
    check_tfvars_exists "$tfvars"
    
    log_warn "About to apply changes to $environment environment"
    if [ "$NO_CONFIRM" != "true" ]; then
        read -p "Are you sure? (yes/no): " -r
        if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            log_info "Operation cancelled"
            exit 0
        fi
    fi
    
    log_info "Applying infrastructure for $environment..."
    cd "$TERRAFORM_DIR"
    terraform apply -var-file="$tfvars" "${extra_args[@]}"
    cd - > /dev/null
    
    log_success "Infrastructure applied successfully"
    log_info "Run: $0 $environment output  (to see cluster details)"
}

terraform_destroy() {
    local environment=$1
    shift
    local extra_args=("$@")
    
    local tfvars=$(get_tfvars_file "$environment")
    check_tfvars_exists "$tfvars"
    
    log_warn "WARNING: This will destroy all resources in $environment"
    if [ "$NO_CONFIRM" != "true" ]; then
        read -p "Type 'destroy-$environment' to confirm: " -r
        if [[ ! $REPLY == "destroy-$environment" ]]; then
            log_info "Destruction cancelled"
            exit 0
        fi
    fi
    
    log_info "Destroying infrastructure for $environment..."
    cd "$TERRAFORM_DIR"
    terraform destroy -var-file="$tfvars" "${extra_args[@]}"
    cd - > /dev/null
    
    log_success "Infrastructure destroyed"
}

terraform_output() {
    local environment=$1
    
    local tfvars=$(get_tfvars_file "$environment")
    check_tfvars_exists "$tfvars"
    
    log_info "Terraform outputs for $environment:"
    cd "$TERRAFORM_DIR"
    terraform output -json
    cd - > /dev/null
}

terraform_refresh() {
    local environment=$1
    
    local tfvars=$(get_tfvars_file "$environment")
    check_tfvars_exists "$tfvars"
    
    log_info "Refreshing state for $environment..."
    cd "$TERRAFORM_DIR"
    terraform refresh -var-file="$tfvars"
    cd - > /dev/null
}

configure_kubectl() {
    local environment=$1
    
    # Extract cluster name from state
    cd "$TERRAFORM_DIR"
    local cluster_name=$(terraform output -raw eks_cluster_name 2>/dev/null || echo "aws-info-website-$environment")
    cd - > /dev/null
    
    local region=$(grep "region" "environments/${environment}.tfvars" | grep -o '"[^"]*"' | head -1 | tr -d '"')
    region=${region:-"us-east-1"}
    
    log_info "Configuring kubectl for $cluster_name..."
    aws eks update-kubeconfig \
        --region "$region" \
        --name "$cluster_name"
    
    log_success "kubectl configured for $cluster_name"
    kubectl cluster-info
}

################################################################################
# Main Script
################################################################################

# Default values
NO_CONFIRM=false
EXTRA_ARGS=()

# Parse command line arguments
if [ $# -eq 0 ]; then
    print_usage
fi

ENVIRONMENT=""
ACTION=""

while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help)
            print_usage
            ;;
        -v|--var)
            shift
            if [ -z "$1" ]; then
                log_error "Missing value for --var"
                exit 1
            fi
            EXTRA_ARGS+=("-var" "$1")
            shift
            ;;
        --target)
            shift
            if [ -z "$1" ]; then
                log_error "Missing value for --target"
                exit 1
            fi
            EXTRA_ARGS+=("-target" "$1")
            shift
            ;;
        --no-confirm)
            NO_CONFIRM=true
            shift
            ;;
        dev|staging|prod|production)
            if [ "$1" == "prod" ]; then
                ENVIRONMENT="production"
            else
                ENVIRONMENT="$1"
            fi
            shift
            ;;
        plan|apply|destroy|output|refresh)
            ACTION="$1"
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            print_usage
            ;;
    esac
done

# Validate inputs
if [ -z "$ENVIRONMENT" ]; then
    log_error "Environment not specified"
    print_usage
fi

if [ -z "$ACTION" ]; then
    log_error "Action not specified"
    print_usage
fi

validate_environment "$ENVIRONMENT"
validate_action "$ACTION"

# Check prerequisites
check_prerequisites

# Initialize Terraform
terraform_init

# Execute action
case "$ACTION" in
    plan)
        terraform_plan "$ENVIRONMENT" "${EXTRA_ARGS[@]}"
        ;;
    apply)
        terraform_apply "$ENVIRONMENT" "${EXTRA_ARGS[@]}"
        configure_kubectl "$ENVIRONMENT"
        ;;
    destroy)
        terraform_destroy "$ENVIRONMENT" "${EXTRA_ARGS[@]}"
        ;;
    output)
        terraform_output "$ENVIRONMENT"
        ;;
    refresh)
        terraform_refresh "$ENVIRONMENT"
        ;;
esac

log_success "Operation completed successfully"
