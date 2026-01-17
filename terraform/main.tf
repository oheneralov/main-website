################################################################################
# Networking helpers
################################################################################

data "http" "terraform_client_ip" {
  count = var.cluster_endpoint_public_access && length(var.cluster_endpoint_public_access_cidrs) == 0 ? 1 : 0
  url   = "https://checkip.amazonaws.com/"
}

locals {
  detected_public_cidr = length(data.http.terraform_client_ip) > 0 ? format("%s/32", chomp(data.http.terraform_client_ip[0].response_body)) : null
}

################################################################################
# EKS Cluster Creation
################################################################################

resource "aws_eks_cluster" "main" {
  name                      = var.cluster_name
  version                   = var.kubernetes_version
  role_arn                  = aws_iam_role.eks_cluster_role.arn
  enabled_cluster_log_types = var.cluster_log_types

  vpc_config {
    subnet_ids              = var.subnet_ids
    endpoint_private_access = true
    endpoint_public_access  = var.cluster_endpoint_public_access
    public_access_cidrs     = local.eks_cluster_public_access_cidrs
    security_group_ids      = var.cluster_security_group_ids
  }

  tags = merge(
    var.common_labels,
    {
      Name        = var.cluster_name
      Environment = var.environment
    }
  )

  depends_on = [aws_iam_role_policy_attachment.eks_cluster_policy]
}

################################################################################
# EKS Node Group
################################################################################

resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${var.cluster_name}-node-group"
  node_role_arn   = aws_iam_role.eks_node_role.arn
  subnet_ids      = var.subnet_ids
  version         = var.kubernetes_version

  scaling_config {
    min_size     = var.node_group_min_size
    max_size     = var.node_group_max_size
    desired_size = var.node_group_desired_size
  }

  instance_types = var.node_instance_types
  disk_size      = var.node_disk_size

  tags = merge(
    var.common_labels,
    {
      Name        = "${var.cluster_name}-node-group"
      Environment = var.environment
    }
  )

  depends_on = [
    aws_iam_role_policy_attachment.eks_node_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.eks_container_registry_policy
  ]
}

################################################################################
# IAM Roles and Policies
################################################################################

# EKS Cluster Role
resource "aws_iam_role" "eks_cluster_role" {
  name = "${var.cluster_name}-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(
    var.common_labels,
    {
      Name = "${var.cluster_name}-cluster-role"
    }
  )
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster_role.name
}

# EKS Node Role
resource "aws_iam_role" "eks_node_role" {
  name = "${var.cluster_name}-node-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(
    var.common_labels,
    {
      Name = "${var.cluster_name}-node-role"
    }
  )
}

resource "aws_iam_role_policy_attachment" "eks_node_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.eks_node_role.name
}

resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.eks_node_role.name
}

resource "aws_iam_role_policy_attachment" "eks_container_registry_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.eks_node_role.name
}

################################################################################
# Reference created cluster metadata
################################################################################

locals {
  eks_cluster_name                  = aws_eks_cluster.main.name
  eks_cluster_endpoint              = aws_eks_cluster.main.endpoint
  eks_cluster_ca_data               = aws_eks_cluster.main.certificate_authority[0].data
  eks_cluster_arn                   = aws_eks_cluster.main.arn
  eks_cluster_public_access_cidrs   = var.cluster_endpoint_public_access ? (length(var.cluster_endpoint_public_access_cidrs) > 0 ? var.cluster_endpoint_public_access_cidrs : compact([local.detected_public_cidr])) : []
}

provider "kubernetes" { # Configure the Kubernetes provider to interact with the EKS cluster
  host                   = local.eks_cluster_endpoint
  cluster_ca_certificate = base64decode(local.eks_cluster_ca_data)

  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args = [
      "eks",
      "get-token",
      "--cluster-name", local.eks_cluster_name,
      "--region", var.region
    ]
  }
}

################################################################################
# See helm.tf for:
# - Helm provider configuration
# - Helm release definitions
# - Kubernetes namespace management
#
# See helm-variables.tf for:
# - Helm-specific variables
# - Chart configuration options
# - Deployment behavior settings
#
# See helm-outputs.tf for:
# - Helm release status outputs
# - Useful Helm and kubectl commands

################################################################################
# S3 Bucket for Application Data
################################################################################

resource "aws_s3_bucket" "app_data" {
  bucket = var.s3_bucket_name

  tags = merge(
    var.common_labels,
    {
      Name        = var.s3_bucket_name
      Environment = var.environment
      Purpose     = "Application Data Storage"
    }
  )
}

resource "aws_s3_bucket_versioning" "app_data" {
  bucket = aws_s3_bucket.app_data.id

  versioning_configuration {
    status = var.s3_versioning_enabled ? "Enabled" : "Suspended"
  }
}

resource "aws_s3_bucket_public_access_block" "app_data" {
  bucket = aws_s3_bucket.app_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

