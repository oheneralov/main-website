# Helm Chart Test Suite Documentation

## Overview

This Helm chart includes a comprehensive test suite that validates deployment configuration, connectivity, security, and resource management. Tests are designed to run after chart installation to ensure everything is configured correctly.

## Test Files

### 1. **test-connection.yaml**
**Purpose**: Basic connectivity testing  
**Tests**:
- Mainwebsite service reachability
- HTTP response verification

**Run**:
```bash
helm test mainwebsite -n production
```

### 2. **test-mainwebsite.yaml**
**Purpose**: Mainwebsite deployment connectivity  
**Tests**:
- Service DNS resolution
- HTTP GET request to mainwebsite pod
- Service health status

**Conditions**: Runs only if `mainwebsite.enabled: true`

### 3. **test-labels.yaml**
**Purpose**: Verify Kubernetes labels and selectors  
**Tests**:
- Deployment label verification
- Pod label verification
- Service selector verification
- Label consistency across resources

**Conditions**: Runs only if `mainwebsite.enabled: true`

**Verifies**:
- Standard Kubernetes labels (app.kubernetes.io/*)
- Release name labels
- Component labels
- Service-to-pod selector matching

### 4. **test-rbac.yaml**
**Purpose**: Verify RBAC resource creation  
**Tests**:
- ServiceAccount exists
- ClusterRole exists and has permissions
- ClusterRoleBinding exists and is correctly bound

**Conditions**: Runs only if `rbac.create: true`

**Verifies**:
- RBAC resources are properly created
- ServiceAccount is bound to roles
- Permissions are granted

### 5. **test-hpa.yaml**
**Purpose**: Verify HorizontalPodAutoscaler configuration  
**Tests**:
- Mainwebsite HPA resource exists
- HPA status and configuration

**Conditions**: Runs only if autoscaling is enabled

**Verifies**:
- HPA resources created correctly
- Min/max replicas configured
- Autoscaling metric targets configured
- HPA status shows ready

### 6. **test-ingress.yaml**
**Purpose**: Verify Ingress/IngressRoute configuration  
**Tests**:
- Mainwebsite IngressRoute exists
- Hostname rules configured correctly

**Conditions**: Runs only if `ingress.enabled: true`

**Verifies**:
- IngressRoute resources created
- Hostname rules match configuration
- Service references are correct
- EntryPoints configured

### 7. **test-monitoring.yaml**
**Purpose**: Verify Prometheus monitoring integration  
**Tests**:
- Mainwebsite ServiceMonitor exists
- Scrape paths and intervals configured

**Conditions**: Runs only if `monitoring.serviceMonitor.enabled: true`

**Verifies**:
- ServiceMonitor CRDs created
- Prometheus scrape configuration
- Scrape endpoints configured
- Label selectors match pods

### 8. **test-resources.yaml**
**Purpose**: Verify resource requests and limits  
**Tests**:
- CPU and memory limits configured
- CPU and memory requests configured
- Resources match values.yaml configuration

**Verifies**:
- Resource limits properly set
- Resource requests properly set
- Values applied correctly to pods
- No resource conflicts

### 9. **test-security.yaml**
**Purpose**: Verify security context configuration  
**Tests**:
- Pod security context applied
- Container security context applied
- Non-root user execution
- Privilege escalation disabled
- Read-only filesystem configured

**Verifies**:
- Running as non-root user (UID from values)
- Privilege escalation disabled
- Read-only filesystem where configured
- Security contexts applied correctly

## Running Tests

### Run All Tests
```bash
# Run all tests (blocks until complete)
helm test mainwebsite -n production

# Run all tests (non-blocking)
helm test mainwebsite -n production --timeout 5m
```

### Run Specific Test
```bash
# Get test pod name and logs
kubectl logs -f <test-pod-name> -n production

# Describe test pod for details
kubectl describe pod <test-pod-name> -n production
```

### View Test Results
```bash
# Get test pod status
kubectl get pods -n production -l helm.sh/hook=test

# View test logs
kubectl logs <test-pod-name> -n production

# Get test pod details
kubectl describe pod <test-pod-name> -n production
```

## Test Execution Flow

```
helm test
    ↓
1. test-connection.yaml (basic connectivity)
    ↓
2. test-mainwebsite.yaml (mainwebsite service)
    ↓
3. test-labels.yaml (label verification)
  ↓
4. test-rbac.yaml (RBAC resources)
  ↓
5. test-hpa.yaml (autoscaling)
  ↓
6. test-ingress.yaml (ingress routing)
  ↓
7. test-monitoring.yaml (monitoring)
  ↓
8. test-resources.yaml (resource config)
  ↓
9. test-security.yaml (security context)
    ↓
Result: PASS or FAIL
```

## Test Cleanup

### Automatic Cleanup
Tests are automatically cleaned up after execution based on the `helm.sh/hook-delete-policy` annotation:
```yaml
annotations:
  "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
```

This means:
- Test pods are deleted if they succeed
- Test pods are re-created on next test run
- Failed test pods are kept for debugging

### Manual Cleanup
```bash
# Delete all test pods
kubectl delete pods -n production -l helm.sh/hook=test

# Delete specific test
kubectl delete pod <test-pod-name> -n production
```

## Troubleshooting Tests

### Test: Connection Failed
```bash
# Check service exists
kubectl get svc -n production

# Check service endpoints
kubectl get endpoints -n production

# Check pods are running
kubectl get pods -n production

# Try port-forward
kubectl port-forward svc/mainwebsite-mainwebsite 3000:80 -n production
```

### Test: RBAC Failed
```bash
# Verify ServiceAccount
kubectl get serviceaccount -n production

# Verify ClusterRole
kubectl get clusterrole | grep mainwebsite

# Verify ClusterRoleBinding
kubectl get clusterrolebinding | grep mainwebsite

# Check role permissions
kubectl describe clusterrole mainwebsite
```

### Test: HPA Failed
```bash
# Check HPA exists
kubectl get hpa -n production

# Check HPA status
kubectl describe hpa mainwebsite-mainwebsite -n production

# Check metrics server
kubectl get deployment metrics-server -n kube-system
```

### Test: Monitoring Failed
```bash
# Check ServiceMonitor exists
kubectl get servicemonitor -n production

# Check ServiceMonitor config
kubectl describe servicemonitor mainwebsite-mainwebsite -n production

# Check Prometheus Operator
kubectl get deployment prometheus-operator -n monitoring
```

## Test Results Interpretation

### Successful Test Output
```
✓ Service is healthy
✓ All RBAC resources verified
✓ All HPA resources verified
✓ All Ingress resources verified
✓ All monitoring resources verified
✓ All resource configurations verified
✓ All security contexts verified
```

### Failed Test Output
```
✗ Service connection failed
✗ ServiceAccount not found
✗ ClusterRole not found
✗ HPA not found
✗ IngressRoute not found
✗ ServiceMonitor not found
```

## Test Requirements

### Required Images
- `curlimages/curl:latest` - HTTP connectivity testing
- `bitnami/kubectl:latest` - Kubernetes resource verification

### Required Permissions
Tests require the following Kubernetes permissions:
- `pods: get, create, delete`
- `services: get`
- `deployments: get`
- `horizontalpodautoscalers: get`
- `ingressroutes: get`
- `servicemonitors: get`
- `serviceaccounts: get`
- `clusterroles: get`
- `clusterrolebindings: get`

### Required Cluster Components
For full test suite to work:
- Kubernetes 1.19+
- Prometheus Operator (for ServiceMonitor tests)
- Traefik (for IngressRoute tests)
- Metrics Server (for HPA tests - optional)

## Integration with CI/CD

### GitHub Actions Example
```yaml
- name: Run Helm Tests
  run: |
    helm test mainwebsite -n production --timeout 10m
```

### GitLab CI Example
```yaml
test_helm:
  script:
    - helm test mainwebsite -n production --timeout 10m
```

### Jenkins Example
```groovy
stage('Test') {
  steps {
    sh 'helm test mainwebsite -n production --timeout 10m'
  }
}
```

## Test Best Practices

1. **Run Before Production**: Always run tests in staging before production
2. **Check Test Logs**: Review test logs for warnings even if tests pass
3. **Use Proper Namespaces**: Tests respect namespace configuration
4. **Monitor Test Execution**: Watch for test timeouts or resource issues
5. **Keep Tests Updated**: Update tests when adding new features
6. **Document Test Changes**: Explain why tests are modified

## Extending Tests

### Adding New Tests

Create a new file in `templates/tests/`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "helm-dir.fullname" . }}-test-feature"
  labels:
    {{- include "helm-dir.labels" . | nindent 4 }}
  annotations:
    "helm.sh/hook": test
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
spec:
  containers:
    - name: test
      image: your-test-image:latest
      command:
        - sh
        - -c
        - |
          echo "Testing your feature..."
          # Your test logic here
  restartPolicy: Never
```

### Test Naming Convention
- `test-*.yaml` - Test pod definition
- Use descriptive names
- One test per file
- Use conditional rendering (`{{- if }}`)

## Test Coverage

| Component | Test | Coverage |
|-----------|------|----------|
| Deployments | ✓ test-mainwebsite.yaml | 100% |
| Services | ✓ test-connection.yaml | 100% |
| Ingress | ✓ test-ingress.yaml | 100% |
| HPA | ✓ test-hpa.yaml | 100% |
| RBAC | ✓ test-rbac.yaml | 100% |
| Security | ✓ test-security.yaml | 100% |
| Monitoring | ✓ test-monitoring.yaml | 100% |
| Resources | ✓ test-resources.yaml | 100% |
| Labels | ✓ test-labels.yaml | 100% |

## Related Documentation

- [Helm Testing](https://helm.sh/docs/helm/helm_test/)
- [Helm Hooks](https://helm.sh/docs/topics/charts_hooks/)
- [Kubernetes Pod Hooks](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#container-hooks)
- [Testing Best Practices](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)

