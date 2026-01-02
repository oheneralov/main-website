# EKS Cluster Management - Quick Reference

## Deployment Commands

### Using Deployment Scripts

#### Bash (Linux/Mac)
```bash
# Plan deployment
./eks-deploy.sh dev plan

# Apply deployment
./eks-deploy.sh dev apply

# Destroy resources
./eks-deploy.sh dev destroy

# View outputs
./eks-deploy.sh dev output

# With options
./eks-deploy.sh prod plan --target aws_eks_node_group.main
./eks-deploy.sh staging apply -v node_group_desired_size=5
```

#### PowerShell (Windows)
```powershell
# Plan deployment
.\eks-deploy.ps1 -Environment dev -Action plan

# Apply deployment
.\eks-deploy.ps1 -Environment dev -Action apply

# Destroy resources
.\eks-deploy.ps1 -Environment prod -Action destroy

# View outputs
.\eks-deploy.ps1 -Environment staging -Action output

# With options
.\eks-deploy.ps1 -Environment prod -Action apply -Variables "node_group_desired_size=5"
.\eks-deploy.ps1 -Environment dev -Action plan -Target aws_eks_node_group.main
```

### Using Terraform Directly

```bash
# Initialize
terraform init

# Plan
terraform plan -var-file="environments/dev.tfvars"

# Apply
terraform apply -var-file="environments/dev.tfvars"

# Destroy
terraform destroy -var-file="environments/dev.tfvars"

# Show outputs
terraform output
terraform output eks_cluster_endpoint
terraform output -json

# Refresh state
terraform refresh -var-file="environments/dev.tfvars"

# Target specific resource
terraform apply -var-file="environments/dev.tfvars" -target=aws_eks_cluster.main

# Taint resource (force recreation)
terraform taint aws_eks_node_group.main
terraform apply -var-file="environments/dev.tfvars"
```

## kubectl Commands

### Cluster Information
```bash
# Get cluster info
kubectl cluster-info

# Check cluster health
kubectl get cs

# Get nodes
kubectl get nodes
kubectl get nodes -o wide
kubectl get nodes --show-labels
kubectl top nodes

# Describe a node
kubectl describe node <node-name>
```

### Namespaces
```bash
# List namespaces
kubectl get namespaces

# Create namespace
kubectl create namespace custom-ns

# Set default namespace
kubectl config set-context --current --namespace=production
```

### Pods
```bash
# List pods
kubectl get pods -A
kubectl get pods -n development
kubectl get pods --all-namespaces

# Get pod details
kubectl describe pod <pod-name> -n development

# View pod logs
kubectl logs <pod-name> -n development
kubectl logs <pod-name> -n development --tail=50
kubectl logs <pod-name> -n development -f  # Follow logs

# Execute command in pod
kubectl exec -it <pod-name> -n development -- bash

# Copy files from pod
kubectl cp development/<pod-name>:/path/to/file ./local-file
```

### Deployments
```bash
# List deployments
kubectl get deployments -n development

# Describe deployment
kubectl describe deployment mainwebsite -n development

# Scale deployment
kubectl scale deployment mainwebsite --replicas=5 -n development

# Update image
kubectl set image deployment/mainwebsite mainwebsite=myregistry/myapp:v2 -n development

# Rollout status
kubectl rollout status deployment/mainwebsite -n development

# Rollout history
kubectl rollout history deployment/mainwebsite -n development

# Rollback
kubectl rollout undo deployment/mainwebsite -n development
```

### Services
```bash
# List services
kubectl get services -n development

# Describe service
kubectl describe service mainwebsite -n development

# Port forward
kubectl port-forward svc/mainwebsite 8080:80 -n development

# Get external IP
kubectl get svc mainwebsite -n development
```

### Events
```bash
# Get cluster events
kubectl get events

# Get namespace events
kubectl get events -n development

# Watch events
kubectl get events -n development --watch
```

## Helm Commands

### Release Management
```bash
# List releases
helm list -A
helm list -n development

# Get release status
helm status mainwebsite -n development

# Get release values
helm get values mainwebsite -n development

# Get all release info
helm get all mainwebsite -n development

# Upgrade release
helm upgrade mainwebsite ../helm-dir -n development

# Upgrade with new values
helm upgrade mainwebsite ../helm-dir -n development \
  --set mainwebsite.replicaCount=5

# Rollback release
helm rollback mainwebsite -n development

# Uninstall release
helm uninstall mainwebsite -n development
```

## AWS CLI Commands

### EKS Operations
```bash
# List clusters
aws eks list-clusters

# Describe cluster
aws eks describe-cluster --name aws-info-website-dev

# Get cluster status
aws eks describe-cluster \
  --name aws-info-website-dev \
  --query 'cluster.status' \
  --output text

# List node groups
aws eks list-nodegroups --cluster-name aws-info-website-dev

# Describe node group
aws eks describe-nodegroup \
  --cluster-name aws-info-website-dev \
  --nodegroup-name aws-info-website-dev-node-group

# Update cluster version
aws eks update-cluster-version \
  --name aws-info-website-dev \
  --kubernetes-version 1.29

# Update kubeconfig
aws eks update-kubeconfig \
  --region us-east-1 \
  --name aws-info-website-dev
```

### Subnet Lookup
```bash
# List subnets
aws ec2 describe-subnets

# Get subnets with tags
aws ec2 describe-subnets \
  --filters "Name=tag:kubernetes.io/cluster/aws-info-website-dev,Values=shared" \
  --query 'Subnets[].[SubnetId,AvailabilityZone,CidrBlock]' \
  --output table

# Add tags to subnets
aws ec2 create-tags \
  --resources subnet-12345678 \
  --tags Key=kubernetes.io/cluster/aws-info-website-dev,Value=shared
```

### IAM Operations
```bash
# List IAM roles
aws iam list-roles

# Describe role
aws iam describe-role --role-name aws-info-website-dev-cluster-role

# Get role trust relationship
aws iam get-role --role-name aws-info-website-dev-cluster-role

# Attach policy
aws iam attach-role-policy \
  --role-name aws-info-website-dev-cluster-role \
  --policy-arn arn:aws:iam::aws:policy/AdditionalPolicy
```

### CloudWatch Logs
```bash
# List log groups
aws logs describe-log-groups | grep eks

# Get cluster logs
aws logs tail /aws/eks/aws-info-website-dev/cluster --follow

# Get specific log stream
aws logs get-log-events \
  --log-group-name /aws/eks/aws-info-website-dev/cluster \
  --log-stream-name api
```

## Troubleshooting Commands

### Cluster Issues
```bash
# Check cluster events
kubectl get events

# Check cluster logs (requires CloudWatch Logs enabled)
aws logs tail /aws/eks/aws-info-website-dev/cluster --follow

# Describe problematic pod
kubectl describe pod <pod-name> -n development

# View pod logs
kubectl logs <pod-name> -n development
```

### Node Issues
```bash
# Check node status
kubectl get nodes
kubectl describe node <node-name>

# Check kubelet logs (SSH to node first)
journalctl -u kubelet -f

# Check node readiness
kubectl get nodes -o jsonpath='{.items[*].status.conditions[?(@.type=="Ready")].status}'
```

### Networking Issues
```bash
# Test pod connectivity
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never -- bash

# Check services
kubectl get svc -A

# Check ingress
kubectl get ingress -A

# Port forward for testing
kubectl port-forward svc/mainwebsite 8080:80 -n development
```

### Storage Issues
```bash
# List PVCs
kubectl get pvc -A

# Describe PVC
kubectl describe pvc <pvc-name> -n development

# List PVs
kubectl get pv
```

## Performance Monitoring

### Node Resources
```bash
# CPU and memory usage
kubectl top nodes
kubectl top nodes --sort-by=memory

# Pod resource usage
kubectl top pods -A
kubectl top pods -n development
```

### Metrics (if metrics-server installed)
```bash
# Check metrics availability
kubectl get deployment metrics-server -n kube-system

# View kubelet metrics
kubectl get --raw /metrics | head
```

### HPA Status (if auto-scaling configured)
```bash
# List HPA resources
kubectl get hpa -A

# Describe HPA
kubectl describe hpa mainwebsite -n development
```

## Configuration Management

### View Configuration
```bash
# Get kubectl config
kubectl config view

# Get context
kubectl config get-contexts

# Get current context
kubectl config current-context
```

### Switch Context
```bash
# List contexts
kubectl config get-contexts

# Switch context
kubectl config use-context arn:aws:eks:us-east-1:ACCOUNT:cluster/aws-info-website-prod
```

### Update kubeconfig
```bash
# Update for new cluster
aws eks update-kubeconfig \
  --region us-east-1 \
  --name aws-info-website-prod \
  --kubeconfig ~/.kube/config
```

## Useful Aliases (for Bash/PowerShell)

### Bash
```bash
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgs='kubectl get svc'
alias kgd='kubectl get deploy'
alias kdp='kubectl describe pod'
alias kl='kubectl logs'
```

### PowerShell
```powershell
Set-Alias -Name k -Value kubectl
Set-Alias -Name kgp -Value 'kubectl get pods'
Set-Alias -Name kgs -Value 'kubectl get svc'
Set-Alias -Name kgd -Value 'kubectl get deploy'
```

## Environment Variables

Set these for easier command execution:

```bash
export AWS_REGION=us-east-1
export CLUSTER_NAME=aws-info-website-dev
export NAMESPACE=development

# Quick commands using env vars
kubectl get pods -n $NAMESPACE
aws eks describe-cluster --name $CLUSTER_NAME
```

## Useful Tools

- **k9s** - Terminal UI for kubectl
- **kubectx** - Switch between contexts easily
- **helm-diff** - See what changes before applying
- **kustomize** - Template management
- **lens** - IDE for Kubernetes
- **AWS CloudWatch Container Insights** - Monitoring and logging

---

For more detailed information, see:
- [EKS_SETUP_GUIDE.md](EKS_SETUP_GUIDE.md) - Complete setup guide
- [K8S_CLUSTER_IMPLEMENTATION.md](K8S_CLUSTER_IMPLEMENTATION.md) - Implementation details
