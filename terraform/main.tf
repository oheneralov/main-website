provider "aws" { # Configure the AWS provider
  region = var.region # AWS region, provided as a variable
}

################################################################################
# EKS Cluster Creation (if create_cluster is true)
################################################################################

resource "aws_eks_cluster" "main" {
  count            = var.create_cluster ? 1 : 0
  name             = var.cluster_name
  version          = var.kubernetes_version
  role_arn         = aws_iam_role.eks_cluster_role[0].arn
  enabled_cluster_log_types = var.cluster_log_types

  vpc_config {
    subnet_ids              = var.subnet_ids
    endpoint_private_access = true
    endpoint_public_access  = var.cluster_endpoint_public_access
    public_access_cidrs     = var.cluster_endpoint_public_access_cidrs
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
  count           = var.create_cluster ? 1 : 0
  cluster_name    = aws_eks_cluster.main[0].name
  node_group_name = "${var.cluster_name}-node-group"
  node_role_arn   = aws_iam_role.eks_node_role[0].arn
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
  count = var.create_cluster ? 1 : 0
  name  = "${var.cluster_name}-cluster-role"

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
  count      = var.create_cluster ? 1 : 0
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster_role[0].name
}

# EKS Node Role
resource "aws_iam_role" "eks_node_role" {
  count = var.create_cluster ? 1 : 0
  name  = "${var.cluster_name}-node-role"

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
  count      = var.create_cluster ? 1 : 0
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.eks_node_role[0].name
}

resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  count      = var.create_cluster ? 1 : 0
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.eks_node_role[0].name
}

resource "aws_iam_role_policy_attachment" "eks_container_registry_policy" {
  count      = var.create_cluster ? 1 : 0
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.eks_node_role[0].name
}

################################################################################
# Reference existing or created cluster
################################################################################

data "aws_eks_cluster" "cluster" {
  name = var.create_cluster ? aws_eks_cluster.main[0].name : var.cluster_name
}

data "aws_eks_cluster_auth" "cluster" {
  name = var.create_cluster ? aws_eks_cluster.main[0].name : var.cluster_name
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
