# Terraform Troubleshooting Guide

Common issues encountered when deploying with Terraform and solutions.

---

## Provider & Authentication Issues

### Error: "Error: Error configuring the Google Cloud Provider"

**Symptoms**: 
```
Error: Error configuring the Google Cloud Provider: google:
credentials must be provided when using default application credentials
```

**Root Causes**:
- Service account JSON file not found
- Invalid path to credentials file
- Missing GOOGLE_APPLICATION_CREDENTIALS environment variable

**Solutions**:

```bash
# Option 1: Specify credentials in tfvars
echo 'credentials_file = "./clever-spirit-terraform-service-account.json"' >> environments/dev.tfvars

# Option 2: Use environment variable
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
terraform plan -var-file="environments/dev.tfvars"

# Option 3: Use gcloud authentication
gcloud auth application-default login
```

**Verification**:
```bash
# Check credentials file exists
ls -la clever-spirit-terraform-service-account.json

# Test GCP access
gcloud auth list
gcloud config list
```

---

### Error: "Error: Error requesting list of clusters"

**Symptoms**:
```
Error: Error requesting list of clusters: googleapi: Error 403: 
Permission 'container.clusters.list' denied on resource...
```

**Root Cause**: Service account lacks necessary GCP IAM permissions

**Solution**:

```bash
# Grant required roles
PROJECT_ID="your-project-id"
SERVICE_ACCOUNT="terraform-sa@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/container.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/compute.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/iam.serviceAccountUser"

# Verify permissions
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --format="table(bindings.role)" \
  --filter="bindings.members:${SERVICE_ACCOUNT}"
```

**Verification**:
```bash
# Check if service account can list clusters
gcloud container clusters list --impersonate-service-account="${SERVICE_ACCOUNT}"
```

---

### Error: "Error: googleapi: Error 403: User does not have permission"

**Symptoms**:
```
Error: googleapi: Error 403: User does not have permission to create clusters...
```

**Root Cause**: Service account doesn't have create permissions

**Solution**:

```bash
# Add Editor role for broader permissions (less secure)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/editor"

# Or grant specific roles:
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/container.clusterAdmin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/compute.instanceAdmin"
```

---

## Kubernetes Connection Issues

### Error: "Error: Unable to connect to Kubernetes cluster"

**Symptoms**:
```
Error: error creating Kubernetes client: invalid configuration: 
no auth info for cluster
```

**Root Cause**: Kubernetes provider not authenticated

**Solution**:

```bash
# Method 1: Configure kubeconfig
gcloud container clusters get-credentials gcp-info-website-prod \
  --region us-central1

# Method 2: Explicitly set in terraform
variable "kubernetes_host" {
  description = "Kubernetes API endpoint"
  type        = string
}

# Method 3: Use data source
data "google_container_cluster" "gke" {
  name   = var.cluster_name
  region = var.region
}

provider "kubernetes" {
  host                   = "https://${data.google_container_cluster.gke.endpoint}"
  cluster_ca_certificate = base64decode(data.google_container_cluster.gke.master_auth[0].cluster_ca_certificate)
  # ... auth config
}
```

**Verification**:
```bash
# Test cluster access
kubectl cluster-info

# Get cluster details
kubectl get nodes

# Verify authentication
kubectl auth can-i create pods
```

---

### Error: "Error: Unable to authenticate with Kubernetes"

**Symptoms**:
```
Error: Kubernetes cluster unreachable: the server has asked for 
the client to provide credentials
```

**Root Cause**: Credential mismatch between kubeconfig and cluster

**Solution**:

```bash
# Regenerate kubeconfig
gcloud container clusters get-credentials gcp-info-website-prod \
  --region us-central1 \
  --project clever-spirit-417020

# Verify context
kubectl config current-context

# Switch context if needed
kubectl config get-contexts
kubectl config use-context gke_clever-spirit-417020_us-central1_gcp-info-website-prod

# Test connectivity
kubectl get namespaces
```

---

## Helm & Chart Issues

### Error: "Error: chart not found"

**Symptoms**:
```
Error: stat ../helm-dir/Chart.yaml: no such file or directory
```

**Root Cause**: Incorrect chart path

**Solution**:

```bash
# Verify chart exists
ls -la ../helm-dir/Chart.yaml

# Verify Chart.yaml content
cat ../helm-dir/Chart.yaml

# Update path in terraform
# Use absolute path or verify relative path
variable "helm_chart_path" {
  default = "/absolute/path/to/helm-dir"
}

# Or fix tfvars
echo 'helm_chart_path = "/full/path/to/gcp-info-website/helm-dir"' >> environments/dev.tfvars
```

**Verification**:
```bash
# Validate chart
helm lint /path/to/helm-dir/

# Test dry-run
helm install test-release /path/to/helm-dir/ --dry-run
```

---

### Error: "Error: the server could not find the requested resource"

**Symptoms**:
```
Error: error getting Kubernetes object: error getting object at 
/api/v1/namespaces/default/services/...
```

**Root Cause**: Helm release not deployed or in wrong namespace

**Solution**:

```bash
# Check Helm releases
helm list --all-namespaces

# Check if release exists
helm status mainwebsite -n default

# List resources in namespace
kubectl get all -n production

# Check deployment status
kubectl describe deployment -n production

# View pod logs
kubectl logs -n production <pod-name>
```

---

### Error: "Error: failed to initialize the Helm client"

**Symptoms**:
```
Error: failed to initialize the Helm client: Get "http://127.0.0.1:8080/api/v1/namespaces":
```

**Root Cause**: Helm can't connect to Kubernetes cluster

**Solution**:

```bash
# Ensure kubeconfig is set
export KUBECONFIG=~/.kube/config

# Test Helm connection
helm list

# Verify Kubernetes connectivity
kubectl cluster-info

# Recreate kubeconfig
gcloud container clusters get-credentials <cluster-name> \
  --region us-central1
```

---

## Terraform State Issues

### Error: "Error acquiring the state lock"

**Symptoms**:
```
Error: Error acquiring the state lock: Error getting object: 
the server could not find the requested resource
```

**Root Cause**: State file locked or corrupted

**Solution**:

```bash
# List state locks
terraform force-unlock <LOCK_ID>

# Backup current state
cp terraform.tfstate terraform.tfstate.backup

# Refresh state
terraform refresh

# Validate state
terraform validate
```

---

### Error: "State has uncommitted resource changes"

**Symptoms**:
```
Error: State has uncommitted resource changes that need to be 
applied or discarded
```

**Root Cause**: Previous operation didn't complete

**Solution**:

```bash
# Apply pending changes
terraform apply -auto-approve

# Or discard pending changes
terraform discard

# Or manually inspect state
terraform state list
terraform state show <resource>
```

---

### Error: "Error: Failed to update Root Module"

**Symptoms**:
```
Error: Failed to update Root Module output after successful resource changes
```

**Root Cause**: Output calculation failed

**Solution**:

```bash
# Check output definitions
terraform output

# Validate outputs exist
terraform validate

# Remove problematic output temporarily
# Edit outputs.tf and comment out failing outputs

# Test individual outputs
terraform output gke_cluster_endpoint
```

---

## Variable & Configuration Issues

### Error: "Invalid or unsupported attribute name"

**Symptoms**:
```
Error: Unsupported argument
on main.tf line 15, in resource "google_container_cluster" "primary":
15: invalid_attribute = "value"

An argument named "invalid_attribute" is not expected here.
```

**Root Cause**: Incorrect resource attribute

**Solution**:

```bash
# Check provider documentation
terraform providers

# Validate syntax
terraform validate

# Use correct resource attributes
# Check Google Provider documentation:
# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/container_cluster

# Format code
terraform fmt -recursive
```

---

### Error: "Error: missing required argument"

**Symptoms**:
```
Error: Missing required argument
on main.tf line 10, in resource "google_container_cluster" "primary":
10: resource "google_container_cluster" "primary" {
   
   Missing argument "cluster_autoscaling"
```

**Solution**:

```bash
# Set required variables
terraform apply -var="cluster_name=value"

# Or add to tfvars file
echo 'cluster_name = "gcp-info-website-prod"' >> environments/prod.tfvars

# Set defaults in variables.tf
variable "cluster_name" {
  default = "gcp-info-website"
}
```

---

### Error: "Error: Invalid value"

**Symptoms**:
```
Error: Invalid value
on environments/prod.tfvars line 5, in mainwebsite_image_tag:
5: mainwebsite_image_tag = ""

The image tag cannot be empty.
```

**Root Cause**: Invalid variable value

**Solution**:

```bash
# Update tfvars with valid value
sed -i 's/mainwebsite_image_tag = ""/mainwebsite_image_tag = "v1.0.0"/' environments/prod.tfvars

# Verify validation rules
grep -A5 "validation" variables.tf

# Test variable validation
terraform validate
```

---

## Deployment Issues

### Error: "Error: Timeout while waiting for Helm release to be active"

**Symptoms**:
```
Error: timeout while waiting for Helm release to be active
```

**Root Cause**: 
- Pods not starting
- Resource constraints
- Image pull errors
- Long initialization

**Solution**:

```bash
# Check pod status
kubectl get pods -n production

# Describe problematic pod
kubectl describe pod <pod-name> -n production

# Check pod events
kubectl get events -n production --sort-by='.lastTimestamp'

# Check pod logs
kubectl logs <pod-name> -n production
kubectl logs <pod-name> -n production --previous  # For crashed pods

# Increase timeout in Helm
helm_timeout = 600  # In environments/*.tfvars

# Check image availability
kubectl describe node
kubectl get images
```

---

### Error: "ImagePullBackOff"

**Symptoms**:
```
Pod Events:
  Back-off pulling image "image:tag"
```

**Root Cause**:
- Image doesn't exist
- Registry authentication failed
- Network connectivity issue

**Solution**:

```bash
# Verify image exists
docker pull gcr.io/project/image:tag

# Check image tag
terraform output -raw mainwebsite_image_tag

# Update image in tfvars
mainwebsite_image_tag = "v1.0.0"

# Check registry access
kubectl describe secrets -n production

# Manually pull to test
gcloud container images describe gcr.io/project/image:tag
```

---

### Error: "CrashLoopBackOff"

**Symptoms**:
```
Pod restarting repeatedly with CrashLoopBackOff status
```

**Root Cause**: 
- Application error
- Missing configuration
- Resource constraints

**Solution**:

```bash
# Check pod logs
kubectl logs <pod-name> -n production -c <container>

# Previous crash logs
kubectl logs <pod-name> -n production --previous

# Describe pod for events
kubectl describe pod <pod-name> -n production

# Check resource allocation
kubectl top pods -n production

# Check environment variables
kubectl get pod <pod-name> -n production -o yaml | grep -A20 env:
```

---

## Resource Issues

### Error: "Error: Insufficient memory"

**Symptoms**:
```
Failed to schedule pod: Insufficient memory
```

**Solution**:

```bash
# Check node capacity
kubectl top nodes

# Check resource requests in Helm
helm get values mainwebsite -n production | grep -A3 resources:

# Increase resource requests
helm_set_values = {
  "mainwebsite.resources.requests.memory" = "512Mi"
  "mainwebsite.resources.limits.memory" = "1Gi"
}

# Or scale cluster
gcloud container clusters resize gcp-info-website-prod --num-nodes 5
```

---

### Error: "Error: Insufficient CPU"

**Symptoms**:
```
Failed to schedule pod: Insufficient cpu
```

**Solution**:

```bash
# Check CPU allocation
kubectl top nodes

# Reduce CPU requests
helm_set_values = {
  "mainwebsite.resources.requests.cpu" = "100m"
  "mainwebsite.resources.limits.cpu" = "500m"
}

# Or add node pool
gcloud container node-pools create high-cpu \
  --cluster gcp-info-website-prod \
  --machine-type n1-standard-4
```

---

## Network & Ingress Issues

### Error: "Error: Unable to reach ingress endpoint"

**Symptoms**:
```
Ingress created but service unreachable via external IP
```

**Root Cause**: 
- Ingress not created
- Service not exposed
- Network policy blocking

**Solution**:

```bash
# Check ingress
kubectl get ingress -n production
kubectl describe ingress mainwebsite-ingress -n production

# Check service
kubectl get svc -n production

# Check external IP assignment
kubectl get svc -n production -o wide

# Check network policies
kubectl get networkpolicies -n production

# Test connectivity
curl -v http://<external-ip>
```

---

### Error: "Error: Invalid Ingress Configuration"

**Symptoms**:
```
Error creating Ingress: error validating data: 
spec.rules[0].host must be a valid DNS subdomain
```

**Solution**:

```bash
# Check ingress hostname
terraform output ingress_hostname

# Update Helm values with valid hostname
helm_set_values = {
  "ingress.hosts[0].host" = "api.gcp-info-website.com"
  "ingress.tls[0].hosts[0]" = "api.gcp-info-website.com"
}

# Verify DNS
nslookup api.gcp-info-website.com
dig api.gcp-info-website.com
```

---

## Debugging Workflow

### Step 1: Identify the Problem

```bash
# Check terraform state
terraform show

# Check recent changes
git diff

# Check cloud console for errors
gcloud container operations list
```

### Step 2: Examine Logs

```bash
# Terraform logs
export TF_LOG=DEBUG
terraform apply -var-file="environments/dev.tfvars"

# Kubernetes logs
kubectl logs -n production -l app=mainwebsite
kubectl events -n production

# GCP logs
gcloud logging read "resource.type=k8s_container" --limit 50
```

### Step 3: Test Components

```bash
# Test Helm chart
helm lint ../helm-dir/
helm template test ../helm-dir/

# Test Kubernetes connectivity
kubectl get nodes
kubectl get namespaces

# Test GCP connectivity
gcloud compute instances list
gcloud container clusters list
```

### Step 4: Isolate Issue

```bash
# Test with minimal plan
terraform plan -var-file="environments/dev.tfvars" -target="kubernetes_namespace.default"

# Test chart deployment manually
helm install test ../helm-dir/ -n test-namespace

# Test cluster access
kubectl auth can-i create deployments
```

### Step 5: Resolve & Verify

```bash
# Apply fix
terraform apply -var-file="environments/dev.tfvars"

# Verify deployment
kubectl get all -n production
kubectl get events -n production

# Check metrics
kubectl top pods -n production
```

---

## Emergency Procedures

### Rollback Failed Deployment

```bash
# List previous Helm releases
helm history mainwebsite -n production

# Rollback to previous release
helm rollback mainwebsite -n production

# Or use Terraform rollback
terraform destroy -var-file="environments/prod.tfvars" -auto-approve
terraform apply -var-file="environments/prod.tfvars"
```

### Emergency Delete Resources

```bash
# Force delete stuck pod
kubectl delete pod <pod-name> -n production --grace-period=0 --force

# Force delete stuck deployment
kubectl delete deployment <deployment-name> -n production --cascade=orphan

# Terraform force unlock
terraform force-unlock <LOCK_ID>

# State manipulation (DANGEROUS - backup first)
cp terraform.tfstate terraform.tfstate.backup
terraform state rm 'google_container_cluster.primary'
```

---

## Prevention Checklist

- [ ] Always plan before apply
- [ ] Use separate environments (dev/staging/prod)
- [ ] Backup state files regularly
- [ ] Test in dev first
- [ ] Use version tags (not "latest")
- [ ] Monitor resource usage
- [ ] Set up alerts for pod failures
- [ ] Review Helm templates before deployment
- [ ] Test Ingress configuration locally
- [ ] Verify IAM permissions before deployment
- [ ] Document custom configurations
- [ ] Use remote state in production
- [ ] Implement CI/CD for consistency

---

## Additional Resources

- [GCP Provider Documentation](https://registry.terraform.io/providers/hashicorp/google/latest)
- [Kubernetes Provider Documentation](https://registry.terraform.io/providers/hashicorp/kubernetes/latest)
- [Helm Provider Documentation](https://registry.terraform.io/providers/hashicorp/helm/latest)
- [GKE Documentation](https://cloud.google.com/kubernetes-engine/docs)
- [Terraform Best Practices](https://cloud.google.com/docs/terraform/best-practices-for-terraform)

---

**Last Updated**: January 2, 2026

## Quick Reference: Common Commands

```bash
# Planning
terraform plan -var-file="environments/dev.tfvars"
terraform validate
terraform fmt -recursive

# Debugging
terraform show
terraform state list
terraform state show <resource>

# Deployment
terraform apply -var-file="environments/dev.tfvars"
terraform destroy -var-file="environments/dev.tfvars"

# Kubernetes
kubectl get pods -n production
kubectl describe pod <name> -n production
kubectl logs <pod-name> -n production

# Helm
helm list --all-namespaces
helm status <release> -n <namespace>
helm get values <release> -n <namespace>

# GCP
gcloud container clusters list
gcloud container operations list
gcloud logging read --limit 50
```
