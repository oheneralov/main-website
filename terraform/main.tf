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

################################################################################
# Helm Configuration
################################################################################
# Helm provider and release configuration moved to dedicated helm.tf file
# This separation improves maintainability and organization
#
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

################################################################################
# RDS MySQL Database
################################################################################

resource "aws_db_instance" "mysql_primary" {
  identifier = "${var.cluster_name}-db"

  # Database engine and version
  engine         = "mysql"
  engine_version = var.rds_engine_version

  # Instance configuration
  instance_class      = var.rds_instance_class
  allocated_storage   = var.rds_allocated_storage
  storage_type        = "gp3"
  storage_encrypted   = true

  # Database credentials
  db_name  = var.rds_database_name
  username = var.rds_master_username
  password = var.rds_master_password

  # Backup and high availability
  backup_retention_period = var.rds_backup_retention_period
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  multi_az               = var.rds_num_read_replicas > 0 ? true : false

  # Network and security
  publicly_accessible = false
  skip_final_snapshot = var.environment != "production" ? true : false
  final_snapshot_identifier = var.environment == "production" ? "${var.cluster_name}-db-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}" : null

  # Logging
  enabled_cloudwatch_logs_exports = ["error", "general", "slowquery"]

  tags = merge(
    var.common_labels,
    {
      Name        = "${var.cluster_name}-mysql-primary"
      Environment = var.environment
      Purpose     = "MySQL Primary Database"
    }
  )

  depends_on = [aws_db_subnet_group.default]
}

# RDS Read Replicas
resource "aws_db_instance" "mysql_replica" {
  count = var.rds_num_read_replicas

  identifier = "${var.cluster_name}-db-replica-${count.index + 1}"

  # Replicate from primary
  replicate_source_db = aws_db_instance.mysql_primary.identifier

  # Instance configuration
  instance_class      = var.rds_instance_class
  storage_encrypted   = true
  publicly_accessible = false

  # Enable automated backups for replicas
  backup_retention_period = 7

  skip_final_snapshot = true

  # Logging
  enabled_cloudwatch_logs_exports = ["error", "slowquery"]

  tags = merge(
    var.common_labels,
    {
      Name        = "${var.cluster_name}-mysql-replica-${count.index + 1}"
      Environment = var.environment
      Purpose     = "MySQL Read Replica"
    }
  )
}

# DB Subnet Group
resource "aws_db_subnet_group" "default" {
  name       = "${var.cluster_name}-db-subnet-group"
  subnet_ids = var.subnet_ids

  tags = merge(
    var.common_labels,
    {
      Name        = "${var.cluster_name}-db-subnet-group"
      Environment = var.environment
    }
  )
}
