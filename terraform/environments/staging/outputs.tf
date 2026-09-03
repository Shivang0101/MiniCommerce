output "alb_dns_name" {
  description = "Public URL of the Application Load Balancer"
  value       = module.alb.alb_dns_name
}

output "vpc_id" {
  description = "ID of the created VPC"
  value       = module.vpc.vpc_id
}

output "rds_endpoint" {
  description = "Endpoint of the RDS PostgreSQL instance"
  value       = module.rds.db_endpoint
}

output "redis_endpoint" {
  description = "Endpoint of the ElastiCache Redis replication group"
  value       = module.elasticache.primary_endpoint_address
}

output "ecs_cluster_name" {
  description = "Name of the ECS Fargate cluster"
  value       = module.ecs.cluster_name
}

output "amp_prometheus_endpoint" {
  description = "Endpoint URL of Amazon Managed Prometheus (AMP) workspace"
  value       = module.observability.amp_prometheus_endpoint
}

output "amg_workspace_endpoint" {
  description = "Dashboard URL of Amazon Managed Grafana (AMG) workspace"
  value       = module.observability.amg_workspace_endpoint
}
