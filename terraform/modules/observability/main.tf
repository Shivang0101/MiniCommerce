# ================================================================================
# TERRAFORM AWS OBSERVABILITY MODULE (AMP & AMG)
# ================================================================================

# 1. Amazon Managed Prometheus (AMP) Workspace
resource "aws_prometheus_workspace" "main" {
  alias = var.workspace_alias

  tags = {
    Environment = var.environment
    Project     = "MiniCommerce"
    ManagedBy   = "Terraform"
  }
}

# 2. IAM Role & Policy for ECS Task Remote Write to AMP
resource "aws_iam_policy" "amp_ingest" {
  name        = "minicommerce-${var.environment}-amp-ingest-policy"
  description = "Allows ECS Fargate containers to remote write metrics to Amazon Managed Prometheus (AMP)"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "aps:RemoteWrite",
          "aps:GetSeries",
          "aps:GetLabels",
          "aps:GetMetricMetadata"
        ]
        Resource = "${aws_prometheus_workspace.main.arn}"
      }
    ]
  })
}

# 3. Amazon Managed Grafana (AMG) Workspace (Optional)
resource "aws_grafana_workspace" "main" {
  count                    = var.enable_grafana ? 1 : 0
  name                     = var.grafana_name
  account_access_type      = "CURRENT_ACCOUNT"
  authentication_providers = ["AWS_SSO"]
  permission_type          = "SERVICE_MANAGED"
  role_arn                 = aws_iam_role.grafana[0].arn
  data_sources             = ["PROMETHEUS"]

  tags = {
    Environment = var.environment
    Project     = "MiniCommerce"
    ManagedBy   = "Terraform"
  }
}

# IAM Role for Managed Grafana
resource "aws_iam_role" "grafana" {
  count = var.enable_grafana ? 1 : 0
  name  = "minicommerce-${var.environment}-grafana-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "grafana.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# IAM Policy Attachment for Grafana to Query AMP
resource "aws_iam_role_policy_attachment" "grafana_amp" {
  count      = var.enable_grafana ? 1 : 0
  role       = aws_iam_role.grafana[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonPrometheusFullAccess"
}

