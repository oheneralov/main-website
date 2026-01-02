# EKS Cluster Architecture & Best Practices

## Cluster Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AWS Account                               │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  VPC (10.0.0.0/16)                                   │   │
│  │                                                       │   │
│  │  ┌─────────────────────────────────────────────────┐ │   │
│  │  │ Public Subnet 1 (10.0.1.0/24) - AZ-a           │ │   │
│  │  │ NAT Gateway                                     │ │   │
│  │  └─────────────────────────────────────────────────┘ │   │
│  │                                                       │   │
│  │  ┌─────────────────────────────────────────────────┐ │   │
│  │  │ Private Subnet 1 (10.0.11.0/24) - AZ-a         │ │   │
│  │  │ ┌──────────────────────────────────────────┐   │ │   │
│  │  │ │ EKS Node 1 (t3.large)                   │   │ │   │
│  │  │ │ ┌─────────────────────────────────────┐ │   │ │   │
│  │  │ │ │ mainwebsite Pod                     │ │   │ │   │
│  │  │ │ │ metrics Pod                         │ │   │ │   │
│  │  │ │ │ kube-proxy, coredns, etc.          │ │   │ │   │
│  │  │ │ └─────────────────────────────────────┘ │   │ │   │
│  │  │ └──────────────────────────────────────────┘   │ │   │
│  │  └─────────────────────────────────────────────────┘ │   │
│  │                                                       │   │
│  │  ┌─────────────────────────────────────────────────┐ │   │
│  │  │ Private Subnet 2 (10.0.12.0/24) - AZ-b         │ │   │
│  │  │ ┌──────────────────────────────────────────┐   │ │   │
│  │  │ │ EKS Node 2 (t3.large)                   │   │ │   │
│  │  │ │ ┌─────────────────────────────────────┐ │   │ │   │
│  │  │ │ │ mainwebsite Pod                     │ │   │ │   │
│  │  │ │ │ metrics Pod                         │ │   │ │   │
│  │  │ │ └─────────────────────────────────────┘ │   │ │   │
│  │  │ └──────────────────────────────────────────┘   │ │   │
│  │  └─────────────────────────────────────────────────┘ │   │
│  │                                                       │   │
│  │  ┌─────────────────────────────────────────────────┐ │   │
│  │  │ Private Subnet 3 (10.0.13.0/24) - AZ-c         │ │   │
│  │  │ ┌──────────────────────────────────────────┐   │ │   │
│  │  │ │ EKS Node 3 (t3.large)                   │   │ │   │
│  │  │ │ ┌─────────────────────────────────────┐ │   │ │   │
│  │  │ │ │ mainwebsite Pod                     │ │   │ │   │
│  │  │ │ │ metrics Pod                         │ │   │ │   │
│  │  │ │ └─────────────────────────────────────┘ │   │ │   │
│  │  │ └──────────────────────────────────────────┘   │ │   │
│  │  └─────────────────────────────────────────────────┘ │   │
│  │                                                       │   │
│  │  ┌─────────────────────────────────────────────────┐ │   │
│  │  │ EKS Control Plane (Managed by AWS)              │ │   │
│  │  │ - API Server                                    │ │   │
│  │  │ - etcd Database                                │ │   │
│  │  │ - Scheduler                                    │ │   │
│  │  │ - Controller Manager                           │ │   │
│  │  │ (Runs in 3 AZs across AWS infrastructure)      │ │   │
│  │  └─────────────────────────────────────────────────┘ │   │
│  │                                                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ CloudWatch Logs                                      │   │
│  │ - API server logs                                   │   │
│  │ - Audit logs                                        │   │
│  │ - Authenticator logs                               │   │
│  │ - Controller manager logs                          │   │
│  │ - Scheduler logs                                   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Environment-Specific Configurations

### Development
```
Cluster: aws-info-website-dev
Kubernetes Version: 1.28
Nodes: 1-3 (desired: 2)
Instance Type: t3.medium
Replicas: 1
Auto-scaling: Minimal
Logging: API, Audit, Authenticator
Endpoint Access: Public (0.0.0.0/0)
Cost: ~$50-100/month
```

### Staging
```
Cluster: aws-info-website-staging
Kubernetes Version: 1.28
Nodes: 2-5 (desired: 3)
Instance Type: t3.medium
Replicas: 2-4
Auto-scaling: Enabled
Logging: API, Audit, Authenticator, Controller Manager
Endpoint Access: Public (0.0.0.0/0)
Cost: ~$100-200/month
```

### Production
```
Cluster: aws-info-website-prod
Kubernetes Version: 1.28
Nodes: 3-20 (desired: 5)
Instance Type: t3.large
Replicas: 3+
Auto-scaling: Aggressive
Logging: All types enabled
Endpoint Access: Restricted by CIDR
Cost: ~$300-600+/month
```

## Best Practices

### 1. High Availability

**Multi-AZ Deployment**
```hcl
# Use subnets in different availability zones
subnet_ids = [
  "subnet-az-a-private",
  "subnet-az-b-private", 
  "subnet-az-c-private"
]
```

**Pod Disruption Budgets**
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: mainwebsite-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: mainwebsite
```

**Anti-Affinity Rules**
```yaml
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values:
            - mainwebsite
        topologyKey: kubernetes.io/hostname
```

### 2. Security

**Network Security**
```hcl
# Restrict cluster endpoint access
cluster_endpoint_public_access = false
# OR restrict to specific IPs
cluster_endpoint_public_access_cidrs = [
  "203.0.113.0/24"  # Your company VPN/office IP
]
```

**RBAC Configuration**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list"]
```

**Network Policies**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: mainwebsite-netpol
spec:
  podSelector:
    matchLabels:
      app: mainwebsite
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8080
```

### 3. Resource Management

**Resource Requests and Limits**
```yaml
containers:
- name: mainwebsite
  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "512Mi"
      cpu: "500m"
```

**Horizontal Pod Autoscaling**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: mainwebsite-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: mainwebsite
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

**Node Group Configuration**
```hcl
# Use multiple instance types for flexibility
node_instance_types = ["t3.large", "t3a.large", "m5.large"]

# Enable auto-scaling
node_group_min_size = 3
node_group_max_size = 20
node_group_desired_size = 5
```

### 4. Monitoring and Logging

**Enable All Logging Types**
```hcl
cluster_log_types = [
  "api",
  "audit",
  "authenticator",
  "controllerManager",
  "scheduler"
]
```

**CloudWatch Monitoring**
```bash
# View control plane logs
aws logs tail /aws/eks/aws-info-website-prod/cluster --follow

# Get specific component logs
aws logs get-log-events \
  --log-group-name /aws/eks/aws-info-website-prod/cluster \
  --log-stream-name audit
```

**Container Insights**
```bash
# Enable CloudWatch Container Insights for detailed metrics
aws eks create-logging --cluster-name aws-info-website-prod \
  --logging-enable componentList=["api", "audit", "authenticator"]
```

### 5. Cost Optimization

**Reserved Instances**
```hcl
# Use consistent instance types to leverage RIs
node_instance_types = ["t3.large"]  # Single type for RI optimization
```

**Spot Instances** (for non-critical workloads)
```hcl
# Add spot instances for cost savings
node_instance_types = ["t3.large", "t3a.large", "t2.large"]
# Configure for spot in node group
```

**Auto-Scaling Policies**
```bash
# Scale down during off-hours
# Set desired_size to 1 for dev environment
```

### 6. Upgrades and Maintenance

**Kubernetes Version Upgrade Process**
```bash
# 1. Update tfvars
# kubernetes_version = "1.29"

# 2. Plan changes
terraform plan -var-file="environments/prod.tfvars"

# 3. Upgrade control plane (automatic with terraform apply)
terraform apply -var-file="environments/prod.tfvars"

# 4. Monitor upgrade
aws eks describe-cluster --name aws-info-website-prod \
  --query 'cluster.platformVersion'

# 5. Upgrade node groups
# This happens automatically with terraform apply
```

**Backup Strategy**
```bash
# Backup cluster configuration
kubectl get all -A -o yaml > cluster-backup.yaml

# Backup Helm releases
helm get values mainwebsite -n production > helm-values-backup.yaml

# EKS etcd: Handled by AWS (automatic backups)
```

### 7. Environment Parity

**Ensure consistent configuration across environments**
```hcl
# Use same Kubernetes version across all environments
kubernetes_version = "1.28"

# Ensure similar networking architecture
# (Same number of AZs, similar CIDR ranges)

# Use environment-specific overrides only for sizing
# Keep core configuration identical
```

## Troubleshooting Checklist

### Cluster Won't Create
- [ ] VPC exists and has internet connectivity
- [ ] Subnets are tagged correctly
- [ ] IAM user has EKS permissions
- [ ] Check AWS CloudTrail for errors
- [ ] Ensure subnet IPs are unique

### Nodes Not Joining Cluster
- [ ] Security group allows node-to-control-plane communication
- [ ] IAM role has correct permissions
- [ ] Kubelet can reach control plane endpoint
- [ ] Check node status: `kubectl describe node <node-name>`
- [ ] Review CloudWatch logs

### Applications Not Running
- [ ] Pod resources meet node availability
- [ ] Image pull secrets configured
- [ ] Security groups allow pod traffic
- [ ] Check pod events: `kubectl describe pod <pod-name>`
- [ ] View logs: `kubectl logs <pod-name>`

### High Latency/Performance Issues
- [ ] Monitor node CPU/memory: `kubectl top nodes`
- [ ] Check pod resources: `kubectl top pods`
- [ ] Review auto-scaling: `kubectl describe hpa`
- [ ] Check network policies blocking traffic
- [ ] Monitor inter-node communication

## Disaster Recovery

### Backup Procedure
```bash
# Daily backup of cluster configuration
0 2 * * * /usr/local/bin/backup-eks-cluster.sh

# Script content:
#!/bin/bash
BACKUP_DIR="/backups/eks/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup all resources
kubectl get all -A -o yaml > $BACKUP_DIR/all-resources.yaml

# Backup Helm releases
helm list -A -o json > $BACKUP_DIR/helm-releases.json
for release in $(helm list -q); do
  helm get values $release > $BACKUP_DIR/values-$release.yaml
done

# Backup ConfigMaps and Secrets (encrypted)
kubectl get configmap -A -o yaml | gpg --encrypt > $BACKUP_DIR/configmaps.yaml.gpg
```

### Recovery Procedure
```bash
# 1. Create new cluster with same configuration
terraform apply -var-file="environments/prod.tfvars"

# 2. Restore configuration
kubectl apply -f /backups/eks/20240115/all-resources.yaml

# 3. Restore Helm releases
helm install mainwebsite ../helm-dir -n production \
  -f /backups/eks/20240115/values-mainwebsite.yaml
```

## Performance Tuning

### Reduce Pod Startup Time
```hcl
# Pre-pull images on nodes
# Use private ECR with IAM roles

# Reduce container size (multi-stage builds)
# Implement readiness probes efficiently
```

### Optimize Resource Usage
```yaml
# Set appropriate resource requests/limits
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi

# Use init containers for setup
initContainers:
- name: setup
  image: myapp:setup
```

## Security Hardening

### Network Segmentation
```hcl
# Use private subnets for nodes
# Implement Network Policies
# Use VPC flow logs for monitoring
```

### Image Security
```bash
# Use ECR scanning
aws ecr start-image-scan --repository-name myapp --image-id imageTag=latest

# Sign images
# Use only approved base images
# Regular CVE scanning
```

---

**Last Updated**: January 2, 2026

For more information:
- [EKS_SETUP_GUIDE.md](EKS_SETUP_GUIDE.md)
- [AWS EKS Best Practices Guide](https://aws.github.io/aws-eks-best-practices/)
- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/)
