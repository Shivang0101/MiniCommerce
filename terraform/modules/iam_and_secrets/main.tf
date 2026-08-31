# AWS IAM Roles & Secrets Manager Module - MiniCommerce Cloud Infrastructure

# 1. IAM Task Execution Role (Allows ECS agent to pull container images and output logs)
resource "aws_iam_role" "execution_role" {
  name = "minicommerce-${var.environment}-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_iam_role_policy_attachment" "execution_policy" {
  role       = aws_iam_role.execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# 2. IAM Task Role (Allows application running inside container to call AWS APIs like Secrets Manager)
resource "aws_iam_role" "task_role" {
  name = "minicommerce-${var.environment}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# 3. AWS Secrets Manager Secret Definitions
resource "aws_secretsmanager_secret" "db_secret" {
  name                    = "minicommerce/${var.environment}/db_password"
  recovery_window_in_days = 0

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_secretsmanager_secret_version" "db_secret_val" {
  secret_id     = aws_secretsmanager_secret.db_secret.id
  secret_string = var.db_password
}

resource "aws_secretsmanager_secret" "redis_secret" {
  name                    = "minicommerce/${var.environment}/redis_auth"
  recovery_window_in_days = 0

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_secretsmanager_secret_version" "redis_secret_val" {
  secret_id     = aws_secretsmanager_secret.redis_secret.id
  secret_string = var.redis_auth_token
}

resource "aws_secretsmanager_secret" "jwt_secret" {
  name                    = "minicommerce/${var.environment}/jwt_secret"
  recovery_window_in_days = 0

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_secretsmanager_secret_version" "jwt_secret_val" {
  secret_id     = aws_secretsmanager_secret.jwt_secret.id
  secret_string = var.jwt_secret
}

# Policy allowing Task Role to read Secrets Manager secrets
resource "aws_iam_policy" "secrets_read_policy" {
  name        = "minicommerce-${var.environment}-secrets-read-policy"
  description = "Allows ECS tasks to read MiniCommerce application secrets"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          aws_secretsmanager_secret.db_secret.arn,
          aws_secretsmanager_secret.redis_secret.arn,
          aws_secretsmanager_secret.jwt_secret.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "task_secrets_attachment" {
  role       = aws_iam_role.task_role.name
  policy_arn = aws_iam_policy.secrets_read_policy.arn
}

resource "aws_iam_role_policy_attachment" "exec_secrets_attachment" {
  role       = aws_iam_role.execution_role.name
  policy_arn = aws_iam_policy.secrets_read_policy.arn
}
