# Docker Build, ECR Push, and Kubernetes Deployment Script (PowerShell)
# 
# This script:
# 1. Builds Docker images for services
# 2. Pushes images to Amazon ECR
# 3. Applies Kubernetes manifests via Helm
#
# Usage: .\deploy-docker-and-k8s.ps1 -Environment <env> -RegistryId <id> [OPTIONS]
#
# Examples:
#   .\deploy-docker-and-k8s.ps1 -Environment dev -RegistryId 123456789012
#   .\deploy-docker-and-k8s.ps1 -Environment dev -RegistryId 123456789012 -SkipDocker
#

param(
    [Parameter(Mandatory=$false)]
    [string]$Region = "us-east-1",
    
    [Parameter(Mandatory=$true)]
    [ValidateSet("dev")]
    [string]$Environment,
    
    [Parameter(Mandatory=$false)]
    [string]$RegistryId = "",
    
    [Parameter(Mandatory=$false)]
    [string]$Namespace = "development",
    
    [Parameter(Mandatory=$false)]
    [string]$HelmChartPath = "../helm-dir",
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipDocker = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipK8s = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$Help = $false
)

# Display help
if ($Help) {
    Write-Host @"
Docker Build, ECR Push, and Kubernetes Deployment Script

Usage: .\deploy-docker-and-k8s.ps1 -Environment <env> -RegistryId <id> [OPTIONS]

Options:
  -Region             AWS region (default: us-east-1)
    -Environment        Environment (dev only) - REQUIRED
  -RegistryId         AWS Account ID for ECR
  -Namespace          Kubernetes namespace (default: development)
  -HelmChartPath      Path to Helm chart (default: ../helm-dir)
  -SkipDocker         Skip Docker build and push
  -SkipK8s            Skip Kubernetes deployment
  -Help               Display this help message

Examples:
    .\deploy-docker-and-k8s.ps1 -Environment dev -RegistryId 123456789012
    .\deploy-docker-and-k8s.ps1 -Environment dev -RegistryId 123456789012 -SkipDocker
"@
    exit 0
}

# Color output functions
function Write-Header {
    param([string]$Message)
    Write-Host "`n================================" -ForegroundColor Blue
    Write-Host $Message -ForegroundColor Blue
    Write-Host "================================`n" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Cyan
}

# Script variables
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$MainwebsiteDir = Join-Path $ProjectRoot "mainwebsite"
$MetricsDir = Join-Path $ProjectRoot "metrics"

# Check prerequisites
function Test-Prerequisites {
    Write-Header "Checking Prerequisites"
    
    $missingTools = @()
    
    # Check Docker
    if (Get-Command docker -ErrorAction SilentlyContinue) {
        Write-Success "Docker is installed"
    } else {
        $missingTools += "docker"
    }
    
    # Check AWS CLI
    if (Get-Command aws -ErrorAction SilentlyContinue) {
        Write-Success "AWS CLI is installed"
    } else {
        $missingTools += "aws"
    }
    
    # Check kubectl
    if (Get-Command kubectl -ErrorAction SilentlyContinue) {
        Write-Success "kubectl is installed"
    } else {
        $missingTools += "kubectl"
    }
    
    # Check Helm
    if (Get-Command helm -ErrorAction SilentlyContinue) {
        Write-Success "Helm is installed"
    } else {
        $missingTools += "helm"
    }
    
    if ($missingTools.Count -gt 0) {
        Write-Error "Missing required tools: $($missingTools -join ', ')"
        Write-Host "Please install the missing tools and try again."
        exit 1
    }
}

# Get ECR login token
function Get-ECRLoginToken {
    Write-Header "Authenticating with ECR"
    
    if ([string]::IsNullOrEmpty($RegistryId)) {
        Write-Error "AWS Account ID (RegistryId) is required for ECR operations!"
        exit 1
    }
    
    $ecrRegistry = "$RegistryId.dkr.ecr.$Region.amazonaws.com"
    Write-Info "Logging into ECR: $ecrRegistry"
    
    try {
        $loginPassword = aws ecr get-login-password --region $Region
        $loginPassword | docker login --username AWS --password-stdin $ecrRegistry
        Write-Success "Successfully authenticated with ECR"
        return $ecrRegistry
    } catch {
        Write-Error "Failed to authenticate with ECR: $_"
        exit 1
    }
}

# Build Docker image
function Build-DockerImage {
    param(
        [string]$ServiceName,
        [string]$DockerfilePath,
        [string]$BuildContext
    )
    
    Write-Header "Building Docker Image: $ServiceName"
    
    if (-not (Test-Path $DockerfilePath)) {
        Write-Error "Dockerfile not found: $DockerfilePath"
        return $null
    }
    
    Write-Info "Build Context: $BuildContext"
    Write-Info "Dockerfile: $DockerfilePath"
    
    $imageTag = "${ServiceName}:latest"
    Write-Info "Building image: $imageTag"
    
    try {
        docker build -f $DockerfilePath -t $imageTag $BuildContext
        Write-Success "Successfully built Docker image: $imageTag"
        return $imageTag
    } catch {
        Write-Error "Failed to build Docker image: $_"
        return $null
    }
}

# Push to ECR
function Push-ToECR {
    param(
        [string]$ServiceName,
        [string]$LocalImageTag,
        [string]$ECRRegistry
    )
    
    Write-Header "Pushing Image to ECR: $ServiceName"
    
    $ecrImageTag = "$ECRRegistry/${ServiceName}:latest"
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $ecrImageTagVersioned = "$ECRRegistry/${ServiceName}:$timestamp"
    
    Write-Info "Local tag: $LocalImageTag"
    Write-Info "ECR tag: $ecrImageTag"
    
    try {
        # Tag the image for ECR
        docker tag $LocalImageTag $ecrImageTag
        docker tag $LocalImageTag $ecrImageTagVersioned
        
        # Push to ECR
        Write-Info "Pushing to ECR..."
        docker push $ecrImageTag
        docker push $ecrImageTagVersioned
        
        Write-Success "Successfully pushed image to ECR"
        Write-Info "Latest: $ecrImageTag"
        Write-Info "Versioned: $ecrImageTagVersioned"
    } catch {
        Write-Error "Failed to push image to ECR: $_"
        return $false
    }
    
    return $true
}

# Deploy Kubernetes manifests
function Deploy-KubernetesManifests {
    Write-Header "Deploying Kubernetes Manifests"
    
    if (-not (Test-Path $HelmChartPath)) {
        Write-Error "Helm chart directory not found: $HelmChartPath"
        exit 1
    }
    
    # Create namespace if it doesn't exist
    Write-Info "Creating/verifying Kubernetes namespace: $Namespace"
    
    try {
        kubectl create namespace $Namespace --dry-run=client -o yaml | kubectl apply -f -
        Write-Success "Namespace ready: $Namespace"
    } catch {
        Write-Error "Failed to create namespace: $_"
        exit 1
    }
    
    # Get the environment-specific values file
    $helmValuesFile = Join-Path $HelmChartPath "values-$Environment.yaml"
    $baseValuesFile = Join-Path $HelmChartPath "values.yaml"
    
    Write-Info "Using Helm chart from: $HelmChartPath"
    
    if (-not (Test-Path $baseValuesFile)) {
        Write-Error "Base values file not found: $baseValuesFile"
        exit 1
    }
    
    # Prepare helm upgrade command
    $helmCmd = "helm upgrade --install mainwebsite"
    $helmCmd += " --namespace $Namespace"
    $helmCmd += " --values $baseValuesFile"
    
    if (Test-Path $helmValuesFile) {
        Write-Info "Using environment-specific values: $helmValuesFile"
        $helmCmd += " --values $helmValuesFile"
    } else {
        Write-Warning "Environment-specific values file not found: $helmValuesFile"
    }
    
    # Update image references in Helm values if ECR registry was pushed
    if (-not $SkipDocker -and -not [string]::IsNullOrEmpty($RegistryId)) {
        $ecrRegistry = "$RegistryId.dkr.ecr.$Region.amazonaws.com"
        Write-Info "Updating Helm values with ECR images from: $ecrRegistry"
        $helmCmd += " --set image.repository=$ecrRegistry/mainwebsite"
        $helmCmd += " --set image.tag=latest"
    }
    
    $helmCmd += " $HelmChartPath"
    
    Write-Info "Executing Helm: $helmCmd"
    
    try {
        Invoke-Expression $helmCmd
        Write-Success "Kubernetes deployment successful"
    } catch {
        Write-Error "Kubernetes deployment failed: $_"
        exit 1
    }
    
    # Verify deployment
    Write-Header "Verifying Deployment"
    Write-Info "Checking rollout status..."
    
    try {
        kubectl rollout status deployment/mainwebsite -n $Namespace --timeout=5m
    } catch {
        Write-Warning "Deployment rollout status check timed out or failed"
        Write-Info "Checking pod status manually..."
    }
    
    Write-Info "Pod Status:"
    kubectl get pods -n $Namespace -ErrorAction SilentlyContinue | Out-Host
    
    Write-Info "Service Status:"
    kubectl get svc -n $Namespace -ErrorAction SilentlyContinue | Out-Host
}

# Main execution
function Main {
    Write-Header "Docker Build, ECR Push, and Kubernetes Deployment"
    
    # Display configuration
    Write-Header "Configuration"
    Write-Host "AWS Region: $Region"
    Write-Host "Environment: $Environment"
    Write-Host "Registry ID: $(if ([string]::IsNullOrEmpty($RegistryId)) { 'Not set' } else { $RegistryId })"
    Write-Host "Kubernetes Namespace: $Namespace"
    Write-Host "Helm Chart Path: $HelmChartPath"
    Write-Host "Skip Docker: $SkipDocker"
    Write-Host "Skip K8s: $SkipK8s`n"
    
    # Check prerequisites
    Test-Prerequisites
    
    # Docker build and push phase
    if (-not $SkipDocker) {
        $ecrRegistry = Get-ECRLoginToken
        
        # Build and push mainwebsite
        $mainwebsiteDockerfile = Join-Path $MainwebsiteDir "Dockerfile"
        $mainwebsiteImage = Build-DockerImage "mainwebsite" $mainwebsiteDockerfile $MainwebsiteDir
        
        if ($mainwebsiteImage) {
            Push-ToECR "mainwebsite" $mainwebsiteImage $ecrRegistry
        }
        
        # Build and push metrics service (if Dockerfile exists)
        $metricsDockerfile = Join-Path $MetricsDir "Dockerfile"
        if (Test-Path $metricsDockerfile) {
            $metricsImage = Build-DockerImage "metrics" $metricsDockerfile $MetricsDir
            if ($metricsImage) {
                Push-ToECR "metrics" $metricsImage $ecrRegistry
            }
        }
    } else {
        Write-Warning "Skipping Docker build and ECR push"
    }
    
    # Kubernetes deployment phase
    if (-not $SkipK8s) {
        Deploy-KubernetesManifests
    } else {
        Write-Warning "Skipping Kubernetes deployment"
    }
    
    Write-Header "Deployment Complete"
    Write-Success "All operations completed successfully!"
}

# Run main function
Main
