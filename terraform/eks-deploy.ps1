# EKS Cluster Deployment Helper Script (PowerShell)
# Usage: .\eks-deploy.ps1 -Environment dev -Action plan

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("dev", "staging", "prod", "production")]
    [string]$Environment,
    
    [Parameter(Mandatory=$true)]
    [ValidateSet("plan", "apply", "destroy", "output", "refresh")]
    [string]$Action,
    
    [string[]]$Variables = @(),
    [string]$Target = "",
    [switch]$NoConfirm = $false
)

# Color functions
function Write-InfoMessage {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-SuccessMessage {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-WarningMessage {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-ErrorMessage {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TerraformDir = $ScriptDir
$Environments = @("dev", "staging", "production")

# Normalize environment
if ($Environment -eq "prod") {
    $Environment = "production"
}

################################################################################
# Functions
################################################################################

function Test-Prerequisites {
    Write-InfoMessage "Checking prerequisites..."
    
    $missing = @()
    
    # Check for required tools
    if (-not (Get-Command terraform -ErrorAction SilentlyContinue)) {
        $missing += "terraform"
    }
    if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
        $missing += "aws"
    }
    if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
        $missing += "kubectl"
    }
    if (-not (Get-Command helm -ErrorAction SilentlyContinue)) {
        $missing += "helm"
    }
    
    if ($missing.Count -gt 0) {
        Write-ErrorMessage "Missing required tools: $($missing -join ', ')"
        exit 1
    }
    
    # Check AWS credentials
    try {
        aws sts get-caller-identity | Out-Null
    }
    catch {
        Write-ErrorMessage "AWS credentials not configured"
        exit 1
    }
    
    Write-SuccessMessage "All prerequisites met"
}

function Get-TfvarsFile {
    param([string]$Env)
    return Join-Path $TerraformDir "environments\${Env}.tfvars"
}

function Test-TfvarsExists {
    param([string]$TfvarsFile)
    if (-not (Test-Path $TfvarsFile)) {
        Write-ErrorMessage "tfvars file not found: $TfvarsFile"
        exit 1
    }
}

function Invoke-TerraformInit {
    Write-InfoMessage "Initializing Terraform..."
    Push-Location $TerraformDir
    terraform init
    Pop-Location
}

function Build-TerraformArgs {
    param([string]$TfvarsFile, [string[]]$Variables, [string]$Target)
    
    $args = @("-var-file=`"$TfvarsFile`"")
    
    if ($Variables.Count -gt 0) {
        foreach ($var in $Variables) {
            $args += "-var"
            $args += "`"$var`""
        }
    }
    
    if ($Target) {
        $args += "-target"
        $args += "`"$Target`""
    }
    
    return $args
}

function Invoke-TerraformPlan {
    param([string]$Environment, [string[]]$Variables, [string]$Target)
    
    $tfvars = Get-TfvarsFile $Environment
    Test-TfvarsExists $tfvars
    
    Write-InfoMessage "Planning infrastructure for $Environment..."
    $args = Build-TerraformArgs $tfvars $Variables $Target
    
    Push-Location $TerraformDir
    terraform plan @args
    Pop-Location
}

function Invoke-TerraformApply {
    param([string]$Environment, [string[]]$Variables, [string]$Target)
    
    $tfvars = Get-TfvarsFile $Environment
    Test-TfvarsExists $tfvars
    
    Write-WarningMessage "About to apply changes to $Environment environment"
    if (-not $NoConfirm) {
        $response = Read-Host "Are you sure? (yes/no)"
        if ($response -ne "yes") {
            Write-InfoMessage "Operation cancelled"
            exit 0
        }
    }
    
    Write-InfoMessage "Applying infrastructure for $Environment..."
    $args = Build-TerraformArgs $tfvars $Variables $Target
    $args += "-auto-approve"
    
    Push-Location $TerraformDir
    terraform apply @args
    Pop-Location
    
    Write-SuccessMessage "Infrastructure applied successfully"
    Write-InfoMessage "Run: .\eks-deploy.ps1 -Environment $Environment -Action output (to see cluster details)"
}

function Invoke-TerraformDestroy {
    param([string]$Environment, [string[]]$Variables, [string]$Target)
    
    $tfvars = Get-TfvarsFile $Environment
    Test-TfvarsExists $tfvars
    
    Write-WarningMessage "WARNING: This will destroy all resources in $Environment"
    if (-not $NoConfirm) {
        $response = Read-Host "Type 'destroy-$Environment' to confirm"
        if ($response -ne "destroy-$Environment") {
            Write-InfoMessage "Destruction cancelled"
            exit 0
        }
    }
    
    Write-InfoMessage "Destroying infrastructure for $Environment..."
    $args = Build-TerraformArgs $tfvars $Variables $Target
    $args += "-auto-approve"
    
    Push-Location $TerraformDir
    terraform destroy @args
    Pop-Location
    
    Write-SuccessMessage "Infrastructure destroyed"
}

function Invoke-TerraformOutput {
    param([string]$Environment)
    
    $tfvars = Get-TfvarsFile $Environment
    Test-TfvarsExists $tfvars
    
    Write-InfoMessage "Terraform outputs for $Environment:"
    Push-Location $TerraformDir
    terraform output -json | ConvertFrom-Json | Format-List
    Pop-Location
}

function Invoke-TerraformRefresh {
    param([string]$Environment, [string[]]$Variables, [string]$Target)
    
    $tfvars = Get-TfvarsFile $Environment
    Test-TfvarsExists $tfvars
    
    Write-InfoMessage "Refreshing state for $Environment..."
    $args = Build-TerraformArgs $tfvars $Variables $Target
    
    Push-Location $TerraformDir
    terraform refresh @args
    Pop-Location
}

function Configure-Kubectl {
    param([string]$Environment)
    
    Write-InfoMessage "Configuring kubectl for $Environment..."
    
    # Try to get cluster name from state
    $clusterName = try {
        Push-Location $TerraformDir
        $output = terraform output -raw eks_cluster_name
        Pop-Location
        $output
    }
    catch {
        "aws-info-website-$Environment"
    }
    
    # Get region from tfvars
    $tfvarsFile = Get-TfvarsFile $Environment
    $region = "us-east-1"
    if (Test-Path $tfvarsFile) {
        $regionLine = Get-Content $tfvarsFile | Select-String 'region\s*=\s*"([^"]*)"'
        if ($regionLine) {
            $region = $regionLine.Matches.Groups[1].Value
        }
    }
    
    Write-InfoMessage "Updating kubeconfig for cluster: $clusterName in region: $region"
    aws eks update-kubeconfig --region $region --name $clusterName
    
    Write-SuccessMessage "kubectl configured for $clusterName"
    kubectl cluster-info
}

################################################################################
# Main Script
################################################################################

try {
    Test-Prerequisites
    Invoke-TerraformInit
    
    switch ($Action) {
        "plan" {
            Invoke-TerraformPlan -Environment $Environment -Variables $Variables -Target $Target
        }
        "apply" {
            Invoke-TerraformApply -Environment $Environment -Variables $Variables -Target $Target
            Configure-Kubectl -Environment $Environment
        }
        "destroy" {
            Invoke-TerraformDestroy -Environment $Environment -Variables $Variables -Target $Target
        }
        "output" {
            Invoke-TerraformOutput -Environment $Environment
        }
        "refresh" {
            Invoke-TerraformRefresh -Environment $Environment -Variables $Variables -Target $Target
        }
    }
    
    Write-SuccessMessage "Operation completed successfully"
}
catch {
    Write-ErrorMessage "An error occurred: $_"
    exit 1
}
