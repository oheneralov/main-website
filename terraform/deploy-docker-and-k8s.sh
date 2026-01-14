#!/bin/bash

################################################################################
# Docker Build, ECR Push, and Kubernetes Deployment Script
################################################################################
# This script:
# 1. Builds Docker images for services
# 2. Pushes images to Amazon ECR
# 3. Applies Kubernetes manifests via Helm
#
# Usage: ./deploy-docker-and-k8s.sh [OPTIONS]
# Options:
#   -r, --region            AWS region (default: us-east-1)
#   -e, --environment       Environment (dev only)
#   -c, --registry-id       AWS Account ID for ECR registry
#   -n, --namespace         Kubernetes namespace (default: development)
#   -h, --helm-chart-path   Path to Helm chart (default: ../helm-dir)
#   -s, --skip-docker       Skip Docker build and push (only apply k8s manifests)
#   -k, --skip-k8s          Skip Kubernetes deployment (only build and push Docker)
#   --help                  Display this help message
#
# Examples:
#   ./deploy-docker-and-k8s.sh --environment dev --registry-id 123456789012
#   ./deploy-docker-and-k8s.sh -e dev -c 123456789012 -s
#
################################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
AWS_REGION="us-east-1"
ENVIRONMENT=""
REGISTRY_ID=""
KUBERNETES_NAMESPACE="development"
HELM_CHART_PATH="../helm-dir"
SKIP_DOCKER=false
SKIP_K8S=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MAINWEBSITE_DIR="$PROJECT_ROOT/mainwebsite"
METRICS_DIR="$PROJECT_ROOT/metrics"

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "\n${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

show_help() {
    head -30 "$0" | tail -25
}

validate_environment() {
    if [[ -z "$ENVIRONMENT" ]]; then
        print_error "Environment is required!"
        echo "Valid values: dev"
        exit 1
    fi
    
    if [[ ! "$ENVIRONMENT" =~ ^(dev)$ ]]; then
        print_error "Invalid environment: $ENVIRONMENT"
        echo "Valid values: dev"
        exit 1
    fi
}

check_prerequisites() {
    print_header "Checking Prerequisites"
    
    local missing_tools=()
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        missing_tools+=("docker")
    else
        print_success "Docker is installed"
    fi
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        missing_tools+=("aws")
    else
        print_success "AWS CLI is installed"
    fi
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        missing_tools+=("kubectl")
    else
        print_success "kubectl is installed"
    fi
    
    # Check Helm
    if ! command -v helm &> /dev/null; then
        missing_tools+=("helm")
    else
        print_success "Helm is installed"
    fi
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        print_error "Missing required tools: ${missing_tools[*]}"
        echo "Please install the missing tools and try again."
        exit 1
    fi
}

get_ecr_login_token() {
    print_header "Authenticating with ECR"
    
    if [[ -z "$REGISTRY_ID" ]]; then
        print_error "AWS Account ID (registry-id) is required for ECR operations!"
        exit 1
    fi
    
    local ecr_registry="${REGISTRY_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
    
    print_info "Logging into ECR: $ecr_registry"
    
    aws ecr get-login-password --region "$AWS_REGION" | \
        docker login --username AWS --password-stdin "$ecr_registry" || {
        print_error "Failed to authenticate with ECR"
        exit 1
    }
    
    print_success "Successfully authenticated with ECR"
    echo "$ecr_registry"
}

build_docker_image() {
    local service_name=$1
    local dockerfile_path=$2
    local build_context=$3
    
    print_header "Building Docker Image: $service_name"
    
    if [[ ! -f "$dockerfile_path" ]]; then
        print_error "Dockerfile not found: $dockerfile_path"
        return 1
    fi
    
    print_info "Build Context: $build_context"
    print_info "Dockerfile: $dockerfile_path"
    
    local image_tag="${service_name}:latest"
    print_info "Building image: $image_tag"
    
    docker build -f "$dockerfile_path" -t "$image_tag" "$build_context" || {
        print_error "Failed to build Docker image: $service_name"
        return 1
    }
    
    print_success "Successfully built Docker image: $image_tag"
    echo "$image_tag"
}

push_to_ecr() {
    local service_name=$1
    local local_image_tag=$2
    local ecr_registry=$3
    
    print_header "Pushing Image to ECR: $service_name"
    
    local ecr_image_tag="${ecr_registry}/${service_name}:latest"
    local ecr_image_tag_versioned="${ecr_registry}/${service_name}:$(date +%Y%m%d-%H%M%S)"
    
    print_info "Local tag: $local_image_tag"
    print_info "ECR tag: $ecr_image_tag"
    
    # Tag the image for ECR
    docker tag "$local_image_tag" "$ecr_image_tag" || {
        print_error "Failed to tag image for ECR"
        return 1
    }
    
    docker tag "$local_image_tag" "$ecr_image_tag_versioned" || {
        print_error "Failed to tag image with version"
        return 1
    }
    
    # Push to ECR
    print_info "Pushing to ECR..."
    docker push "$ecr_image_tag" || {
        print_error "Failed to push image to ECR: $ecr_image_tag"
        return 1
    }
    
    docker push "$ecr_image_tag_versioned" || {
        print_error "Failed to push versioned image to ECR: $ecr_image_tag_versioned"
        return 1
    }
    
    print_success "Successfully pushed image to ECR"
    print_info "Latest: $ecr_image_tag"
    print_info "Versioned: $ecr_image_tag_versioned"
}

deploy_kubernetes_manifests() {
    print_header "Deploying Kubernetes Manifests"
    
    if [[ ! -d "$HELM_CHART_PATH" ]]; then
        print_error "Helm chart directory not found: $HELM_CHART_PATH"
        exit 1
    fi
    
    # Create namespace if it doesn't exist
    print_info "Creating/verifying Kubernetes namespace: $KUBERNETES_NAMESPACE"
    kubectl create namespace "$KUBERNETES_NAMESPACE" --dry-run=client -o yaml | kubectl apply -f - || {
        print_error "Failed to create namespace"
        exit 1
    }
    
    print_success "Namespace ready: $KUBERNETES_NAMESPACE"
    
    # Get the environment-specific values file
    local helm_values_file="${HELM_CHART_PATH}/values-${ENVIRONMENT}.yaml"
    local base_values_file="${HELM_CHART_PATH}/values.yaml"
    
    print_info "Using Helm chart from: $HELM_CHART_PATH"
    
    if [[ ! -f "$base_values_file" ]]; then
        print_error "Base values file not found: $base_values_file"
        exit 1
    fi
    
    # Prepare helm upgrade command
    local helm_cmd="helm upgrade --install mainwebsite"
    helm_cmd="$helm_cmd --namespace $KUBERNETES_NAMESPACE"
    helm_cmd="$helm_cmd --values $base_values_file"
    
    if [[ -f "$helm_values_file" ]]; then
        print_info "Using environment-specific values: $helm_values_file"
        helm_cmd="$helm_cmd --values $helm_values_file"
    else
        print_warning "Environment-specific values file not found: $helm_values_file"
    fi
    
    # Update image references in Helm values if ECR registry was pushed
    if [[ "$SKIP_DOCKER" == "false" && -n "$REGISTRY_ID" ]]; then
        local ecr_registry="${REGISTRY_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        print_info "Updating Helm values with ECR images from: $ecr_registry"
        helm_cmd="$helm_cmd --set image.repository=${ecr_registry}/mainwebsite"
        helm_cmd="$helm_cmd --set image.tag=latest"
    fi
    
    print_info "Executing: $helm_cmd $HELM_CHART_PATH"
    
    if eval "$helm_cmd $HELM_CHART_PATH"; then
        print_success "Kubernetes deployment successful"
    else
        print_error "Kubernetes deployment failed"
        exit 1
    fi
    
    # Verify deployment
    print_header "Verifying Deployment"
    print_info "Checking rollout status..."
    kubectl rollout status deployment/mainwebsite -n "$KUBERNETES_NAMESPACE" --timeout=5m || {
        print_warning "Deployment rollout status check timed out or failed"
        print_info "Checking pod status manually..."
    }
    
    print_info "Pod Status:"
    kubectl get pods -n "$KUBERNETES_NAMESPACE" || true
    
    print_info "Service Status:"
    kubectl get svc -n "$KUBERNETES_NAMESPACE" || true
}

main() {
    print_header "Docker Build, ECR Push, and Kubernetes Deployment"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -r|--region)
                AWS_REGION="$2"
                shift 2
                ;;
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -c|--registry-id)
                REGISTRY_ID="$2"
                shift 2
                ;;
            -n|--namespace)
                KUBERNETES_NAMESPACE="$2"
                shift 2
                ;;
            -h|--helm-chart-path)
                HELM_CHART_PATH="$2"
                shift 2
                ;;
            -s|--skip-docker)
                SKIP_DOCKER=true
                shift
                ;;
            -k|--skip-k8s)
                SKIP_K8S=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Validate environment
    validate_environment
    
    # Display configuration
    print_header "Configuration"
    echo "AWS Region: $AWS_REGION"
    echo "Environment: $ENVIRONMENT"
    echo "Registry ID: ${REGISTRY_ID:-Not set}"
    echo "Kubernetes Namespace: $KUBERNETES_NAMESPACE"
    echo "Helm Chart Path: $HELM_CHART_PATH"
    echo "Skip Docker: $SKIP_DOCKER"
    echo "Skip K8s: $SKIP_K8S"
    
    # Check prerequisites
    check_prerequisites
    
    # Docker build and push phase
    if [[ "$SKIP_DOCKER" == "false" ]]; then
        ECR_REGISTRY=$(get_ecr_login_token)
        
        # Build and push mainwebsite
        MAINWEBSITE_IMAGE=$(build_docker_image "mainwebsite" \
            "$MAINWEBSITE_DIR/Dockerfile" \
            "$MAINWEBSITE_DIR")
        push_to_ecr "mainwebsite" "$MAINWEBSITE_IMAGE" "$ECR_REGISTRY"
        
        # Build and push metrics service (if Dockerfile exists)
        if [[ -f "$METRICS_DIR/Dockerfile" ]]; then
            METRICS_IMAGE=$(build_docker_image "metrics" \
                "$METRICS_DIR/Dockerfile" \
                "$METRICS_DIR")
            push_to_ecr "metrics" "$METRICS_IMAGE" "$ECR_REGISTRY"
        fi
    else
        print_warning "Skipping Docker build and ECR push"
    fi
    
    # Kubernetes deployment phase
    if [[ "$SKIP_K8S" == "false" ]]; then
        deploy_kubernetes_manifests
    else
        print_warning "Skipping Kubernetes deployment"
    fi
    
    print_header "Deployment Complete"
    print_success "All operations completed successfully!"
}

# Run main function
main "$@"
