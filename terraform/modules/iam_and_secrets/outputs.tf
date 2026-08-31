output "execution_role_arn" {
  description = "ARN of the IAM Task Execution Role"
  value       = aws_iam_role.execution_role.arn
}

output "task_role_arn" {
  description = "ARN of the IAM Task Role"
  value       = aws_iam_role.task_role.arn
}

output "db_secret_arn" {
  description = "ARN of the DB password secret"
  value       = aws_secretsmanager_secret.db_secret.arn
}

output "redis_secret_arn" {
  description = "ARN of the Redis AUTH secret"
  value       = aws_secretsmanager_secret.redis_secret.arn
}

output "jwt_secret_arn" {
  description = "ARN of the JWT secret"
  value       = aws_secretsmanager_secret.jwt_secret.arn
}
