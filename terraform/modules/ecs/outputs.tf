output "cluster_name" {
  description = "Name of the created ECS Fargate cluster"
  value       = aws_ecs_cluster.main.name
}

output "cluster_arn" {
  description = "ARN of the created ECS Fargate cluster"
  value       = aws_ecs_cluster.main.arn
}

output "app_security_group_id" {
  description = "Security Group ID of the ECS Fargate Application Tasks"
  value       = aws_security_group.app_tasks.id
}

output "backend_service_name" {
  description = "FastAPI Backend Service name"
  value       = aws_ecs_service.backend.name
}

output "worker_service_name" {
  description = "ARQ Worker Service name"
  value       = aws_ecs_service.worker.name
}

output "frontend_service_name" {
  description = "Nginx Frontend Service name"
  value       = aws_ecs_service.frontend.name
}
