#!/bin/bash
################################################################################
# Helm Deployment Verification Script
# Run this script after Terraform deployment to verify Helm release status
#
# Usage: ./verify-helm-deployment.sh
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration (modify as needed)
RELEASE_NAME="${HELM_RELEASE_NAME:-mainwebsite}"
NAMESPACE="${KUBERNETES_NAMESPACE:-production}"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Helm Deployment Verification${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Function to print status
print_status() {
  local status=$1
  local message=$2
  
  if [ $status -eq 0 ]; then
    echo -e "${GREEN}✓${NC} $message"
  else
    echo -e "${RED}✗${NC} $message"
  fi
}

# Function to print info
print_info() {
  echo -e "${BLUE}ℹ${NC} $1"
}

# Function to print warning
print_warning() {
  echo -e "${YELLOW}⚠${NC} $1"
}

################################################################################
# 1. Check Helm Release
################################################################################
echo -e "${BLUE}1. Checking Helm Release...${NC}"
echo ""

# Check if release exists
if helm list -n "$NAMESPACE" | grep -q "^$RELEASE_NAME"; then
  print_status 0 "Helm release '$RELEASE_NAME' exists"
  
  # Get release status
  RELEASE_STATUS=$(helm status "$RELEASE_NAME" -n "$NAMESPACE" -o json | jq -r '.info.status')
  
  if [ "$RELEASE_STATUS" = "deployed" ]; then
    print_status 0 "Helm release status: $RELEASE_STATUS"
  else
    print_status 1 "Helm release status: $RELEASE_STATUS (Expected: deployed)"
  fi
else
  print_status 1 "Helm release '$RELEASE_NAME' not found"
fi

echo ""

################################################################################
# 2. Check Namespace
################################################################################
echo -e "${BLUE}2. Checking Namespace...${NC}"
echo ""

if kubectl get namespace "$NAMESPACE" &>/dev/null; then
  print_status 0 "Namespace '$NAMESPACE' exists"
  
  # Check namespace status
  NS_PHASE=$(kubectl get namespace "$NAMESPACE" -o jsonpath='{.status.phase}')
  if [ "$NS_PHASE" = "Active" ]; then
    print_status 0 "Namespace status: $NS_PHASE"
  else
    print_status 1 "Namespace status: $NS_PHASE (Expected: Active)"
  fi
else
  print_status 1 "Namespace '$NAMESPACE' not found"
fi

echo ""

################################################################################
# 3. Check Deployments
################################################################################
echo -e "${BLUE}3. Checking Deployments...${NC}"
echo ""

DEPLOYMENTS=$(kubectl get deployments -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}')

if [ -z "$DEPLOYMENTS" ]; then
  print_warning "No deployments found in namespace '$NAMESPACE'"
else
  for deployment in $DEPLOYMENTS; do
    REPLICAS=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{.spec.replicas}')
    READY=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}')
    AVAILABLE=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{.status.availableReplicas}')
    
    if [ "$READY" = "$REPLICAS" ] && [ "$AVAILABLE" = "$REPLICAS" ]; then
      print_status 0 "Deployment '$deployment': $READY/$REPLICAS replicas ready"
    else
      print_status 1 "Deployment '$deployment': $READY/$REPLICAS replicas ready (Available: $AVAILABLE)"
    fi
  done
fi

echo ""

################################################################################
# 4. Check Pods
################################################################################
echo -e "${BLUE}4. Checking Pods...${NC}"
echo ""

PODS=$(kubectl get pods -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}')

if [ -z "$PODS" ]; then
  print_warning "No pods found in namespace '$NAMESPACE'"
else
  FAILED_PODS=0
  for pod in $PODS; do
    POD_STATUS=$(kubectl get pod "$pod" -n "$NAMESPACE" -o jsonpath='{.status.phase}')
    
    if [ "$POD_STATUS" = "Running" ]; then
      print_status 0 "Pod '$pod': $POD_STATUS"
    else
      print_status 1 "Pod '$pod': $POD_STATUS (Expected: Running)"
      FAILED_PODS=$((FAILED_PODS + 1))
    fi
  done
  
  if [ $FAILED_PODS -gt 0 ]; then
    echo ""
    print_warning "$FAILED_PODS pod(s) not running. Use 'kubectl describe pod' for details."
  fi
fi

echo ""

################################################################################
# 5. Check Services
################################################################################
echo -e "${BLUE}5. Checking Services...${NC}"
echo ""

SERVICES=$(kubectl get services -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}')

if [ -z "$SERVICES" ]; then
  print_warning "No services found in namespace '$NAMESPACE'"
else
  for service in $SERVICES; do
    SERVICE_TYPE=$(kubectl get service "$service" -n "$NAMESPACE" -o jsonpath='{.spec.type}')
    CLUSTER_IP=$(kubectl get service "$service" -n "$NAMESPACE" -o jsonpath='{.spec.clusterIP}')
    print_status 0 "Service '$service': Type=$SERVICE_TYPE, ClusterIP=$CLUSTER_IP"
  done
fi

echo ""

################################################################################
# 6. Check Helm Release History
################################################################################
echo -e "${BLUE}6. Checking Helm Release History...${NC}"
echo ""

HISTORY=$(helm history "$RELEASE_NAME" -n "$NAMESPACE" --output json 2>/dev/null || echo "[]")
REVISION_COUNT=$(echo "$HISTORY" | jq 'length')

if [ "$REVISION_COUNT" -gt 0 ]; then
  print_status 0 "Helm release has $REVISION_COUNT revision(s)"
  echo ""
  helm history "$RELEASE_NAME" -n "$NAMESPACE" --output table
else
  print_warning "No release history found"
fi

echo ""

################################################################################
# 7. Check for Recent Errors
################################################################################
echo -e "${BLUE}7. Checking for Recent Errors...${NC}"
echo ""

# Check pod events for errors
ERRORS=$(kubectl get events -n "$NAMESPACE" --field-selector type=Warning,type=Error --sort-by='.lastTimestamp' 2>/dev/null | tail -5)

if [ -z "$ERRORS" ]; then
  print_status 0 "No recent warning or error events"
else
  print_warning "Recent warning/error events found:"
  echo "$ERRORS" | tail -10
fi

echo ""

################################################################################
# 8. Resource Usage
################################################################################
echo -e "${BLUE}8. Resource Usage...${NC}"
echo ""

print_info "Pod resource requests:"
kubectl get pods -n "$NAMESPACE" -o json | jq -r '.items[] | "\(.metadata.name): CPU=\(.spec.containers[0].resources.requests.cpu // "N/A"), Memory=\(.spec.containers[0].resources.requests.memory // "N/A")"'

echo ""

################################################################################
# 9. Summary
################################################################################
echo -e "${BLUE}9. Summary${NC}"
echo ""

# Check overall health
UNHEALTHY=0

# Check release status
if ! helm list -n "$NAMESPACE" | grep -q "^$RELEASE_NAME"; then
  UNHEALTHY=$((UNHEALTHY + 1))
fi

# Check pod status
POD_COUNT=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase!=Running -o json 2>/dev/null | jq '.items | length')
if [ "$POD_COUNT" -gt 0 ]; then
  UNHEALTHY=$((UNHEALTHY + 1))
fi

if [ $UNHEALTHY -eq 0 ]; then
  echo -e "${GREEN}✓ Helm deployment appears healthy!${NC}"
else
  echo -e "${YELLOW}⚠ Some issues detected. Review above for details.${NC}"
fi

echo ""
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Verification Complete${NC}"
echo -e "${BLUE}================================${NC}"

################################################################################
# Additional Helpful Commands
################################################################################
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo ""
echo "Check release values:"
echo "  helm get values $RELEASE_NAME -n $NAMESPACE"
echo ""
echo "View release manifest:"
echo "  helm get manifest $RELEASE_NAME -n $NAMESPACE"
echo ""
echo "View pod logs:"
echo "  kubectl logs -n $NAMESPACE -l app=$RELEASE_NAME -f"
echo ""
echo "Describe pod:"
echo "  kubectl describe pod -n $NAMESPACE <pod-name>"
echo ""
echo "Rollback release:"
echo "  helm rollback $RELEASE_NAME 1 -n $NAMESPACE"
echo ""

exit 0
