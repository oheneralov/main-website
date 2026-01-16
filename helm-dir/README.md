# Mainwebsite Helm Chart

A production-grade Helm chart for deploying the GCP-based website application as a single-service workload on Kubernetes.

## Overview

This chart deploys:
- **mainwebsite**: Primary web application service
- **ServiceMonitor**: Prometheus monitoring integration
- **HPA**: Horizontal Pod Autoscaling (configurable per environment)
- **RBAC**: Service accounts and cluster roles
- **Traefik IngressRoute**: Ingress routing configuration

## Installation

### Prerequisites
- Kubernetes 1.19+
- Helm 3.0+
- Traefik Ingress Controller (optional, for ingress)
- Prometheus Operator (optional, for ServiceMonitor)

### Basic Installation

```bash
# Development
helm install mainwebsite . -f values-dev.yaml

# Staging
helm install mainwebsite . -f values-staging.yaml

# Production
helm install mainwebsite . -f values-prod.yaml
```

### Custom Namespace

```bash
helm install mainwebsite . -f values-prod.yaml -n production
```

## Configuration

### Values Structure

The chart uses a hierarchical values structure for better organization:

```yaml
global:           # Global configuration
mainwebsite:      # Main application service config
monitoring:       # Prometheus monitoring config
ingress:          # Ingress routing config
serviceAccount:   # RBAC configuration
rbac:             # RBAC enablement
```

### Environment-Specific Values

Three pre-configured environment values files are provided:

#### `values-dev.yaml`
- Single replica for the application
- Development image tags (`dev-latest`)
- Reduced resource requests
- Autoscaling disabled
- Dev domain names (dev.oleksandrdesign.com)
- Enhanced SecurityContext for development

#### `values-staging.yaml`
- 2-3 replicas with autoscaling
- Staging image tags (`staging-latest`)
- Moderate resource allocation
- ServiceMonitor enabled
- Staging domain names
- Full SecurityContext enforcement

#### `values-prod.yaml`
- 3+ replicas with aggressive autoscaling (up to 10)
- Explicit version tags (e.g., `1.0.0`)
- Maximum resource requests
- Pod anti-affinity rules for distribution
- PodDisruptionBudgets for high availability
- Production domain names
- Full SecurityContext + SecurityPolicy

## Key Features

### 1. Application Deployment
The mainwebsite workload ships with:
- Dedicated Deployment and Service definitions
- Optional Horizontal Pod Autoscaler per environment
- Explicit resource requests and limits

### 2. Flexible Probes Configuration
Liveness and readiness probes with configurable:
- `initialDelaySeconds`
- `periodSeconds`
- `timeoutSeconds`
- `failureThreshold`

### 3. Monitoring Integration
- ServiceMonitor CRDs for Prometheus
- Configurable metrics port and path

### 4. Ingress Management
- Traefik IngressRoute support
- Per-service hostname configuration
- Middleware support for routing rules
- Automatic service discovery

### 5. RBAC & Security
- ServiceAccount creation
- ClusterRole with minimal permissions
- ClusterRoleBinding automation
- Pod security contexts
- Container security contexts

### 6. High Availability (Production)
- Pod anti-affinity rules
- PodDisruptionBudgets
- Multi-replica deployments
- Horizontal Pod Autoscaler (HPA v2)

## Customization

### Disable RBAC

```yaml
rbac:
  create: false
serviceAccount:
  create: false
```

### Customize Autoscaling

```yaml
mainwebsite:
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 5
    targetCPUUtilizationPercentage: 75
    targetMemoryUtilizationPercentage: 80
```

### Override Image Tags

```bash
helm install mainwebsite . --set mainwebsite.image.tag=v1.2.3
```

### Add Custom Labels

```yaml
global:
  labels:
    team: platform
    cost-center: engineering
```

## Troubleshooting

### Check Deployment Status

```bash
kubectl get deployments -n production
kubectl get pods -n production
kubectl describe pod <pod-name> -n production
```

### View Logs

```bash
kubectl logs -f deployment/mainwebsite-mainwebsite -n production
```

### Verify Services

```bash
kubectl get svc -n production
kubectl get ingress -n production
```

### Check Monitoring

```bash
kubectl get servicemonitor -n production
```

## Best Practices Implemented

✅ **Templating**: Comprehensive use of Helm templates and helpers  
✅ **Labels**: Consistent Kubernetes labels across all resources  
✅ **Namespace Support**: Full namespace templating and support  
✅ **Security**: Pod and container security contexts  
✅ **RBAC**: Service account and role-based access control  
✅ **Observability**: Prometheus integration and monitoring  
✅ **Scalability**: HPA and resource management  
✅ **Reliability**: PodDisruptionBudgets and health checks  
✅ **Environment Separation**: Dev, staging, and production configs  
✅ **Documentation**: Comprehensive inline comments and this README  

## Upgrading

```bash
# Development
helm upgrade mainwebsite . -f values-dev.yaml

# Production with new version
helm upgrade mainwebsite . -f values-prod.yaml --set mainwebsite.image.tag=v1.2.3
```

## Uninstalling

```bash
helm uninstall mainwebsite -n production
```

## File Structure

```
helm-dir/
├── Chart.yaml                      # Chart metadata
├── values.yaml                     # Default values
├── values-dev.yaml                # Dev environment values
├── values-staging.yaml            # Staging environment values
├── values-prod.yaml               # Production environment values
├── templates/
│   ├── _helpers.tpl               # Template helpers
│   ├── deployment.yaml            # Mainwebsite deployment
│   ├── service.yaml               # Service definition
│   ├── ingress.yaml               # Traefik IngressRoute
│   ├── servicemonitor.yaml        # Prometheus ServiceMonitor
│   ├── hpa-mainwebsite.yaml      # Mainwebsite HPA
│   ├── serviceaccount.yaml        # ServiceAccount
│   ├── clusterrole.yaml           # ClusterRole
│   ├── clusterrolebinding.yaml    # ClusterRoleBinding
│   ├── poddisruptionbudget.yaml  # PodDisruptionBudgets
│   ├── NOTES.txt                  # Post-install notes
│   └── tests/
│       └── test-connection.yaml   # Helm test
└── README.md                      # This file
```

## Support & Contribution

For issues or improvements, please contact the platform team or submit a pull request.

---

**Last Updated**: January 2, 2026  
**Chart Version**: 0.1.0  
**App Version**: 1.0.0
