output "primary_endpoint_address" {
  description = "The primary endpoint address for the Redis replication group"
  value       = aws_elasticache_replication_group.main.primary_endpoint_address
}

output "port" {
  description = "The port number of the Redis replication group"
  value       = aws_elasticache_replication_group.main.port
}

output "security_group_id" {
  description = "Security Group ID of the ElastiCache Redis cluster"
  value       = aws_security_group.redis.id
}
