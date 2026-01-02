provider "aws" { # Configure the AWS provider
  region = var.region # AWS region, provided as a variable
}

# Retrieve EKS cluster information
data "aws_eks_cluster" "cluster" {
  name = var.cluster_name # Name of the EKS cluster, provided as a variable
}

data "aws_eks_cluster_auth" "cluster" {
  name = var.cluster_name # Get authentication token for the EKS cluster
}

provider "kubernetes" { # Configure the Kubernetes provider to interact with the EKS cluster
  host                   = data.aws_eks_cluster.cluster.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority[0].data)
  token                  = data.aws_eks_cluster_auth.cluster.token
}

provider "helm" { # Configure the Helm provider to deploy Helm charts to the EKS cluster
  kubernetes {
    host                   = data.aws_eks_cluster.cluster.endpoint
    cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority[0].data)
    token                  = data.aws_eks_cluster_auth.cluster.token
  }
}

resource "helm_release" "mainwebsite" { # Deploy a Helm chart using the Helm provider
  name       = var.helm_release_name   # Name of the Helm release
  chart      = var.helm_chart_path     # Path to the Helm chart directory
  namespace  = var.kubernetes_namespace # Kubernetes namespace to deploy into

  values = [file("${var.helm_chart_path}/values.yaml")] # Load custom values from a YAML file

  timeout = var.helm_timeout
  atomic  = var.helm_atomic_deployment

  dynamic "set" {
    for_each = var.helm_set_values
    content {
      name  = set.key
      value = set.value
    }
  }
}
