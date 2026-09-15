output "amp_workspace_id" {
  value       = aws_prometheus_workspace.main.id
  description = "Amazon Managed Prometheus (AMP) Workspace ID"
}

output "amp_prometheus_endpoint" {
  value       = aws_prometheus_workspace.main.prometheus_endpoint
  description = "Amazon Managed Prometheus (AMP) endpoint URL for metrics ingestion"
}

output "amg_workspace_endpoint" {
  value       = length(aws_grafana_workspace.main) > 0 ? aws_grafana_workspace.main[0].endpoint : "Disabled (Requires AWS Marketplace Subscription & AWS SSO)"
  description = "Amazon Managed Grafana (AMG) Workspace dashboard URL"
}

output "amp_ingest_policy_arn" {
  value       = aws_iam_policy.amp_ingest.arn
  description = "IAM policy ARN for ECS task execution role to remote-write to AMP"
}

