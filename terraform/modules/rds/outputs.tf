output "db_endpoint" {
  description = "The connection endpoint for the RDS PostgreSQL database"
  value       = aws_db_instance.main.endpoint
}

output "db_host" {
  description = "The hostname of the RDS database"
  value       = aws_db_instance.main.address
}

output "db_port" {
  description = "The port of the RDS database"
  value       = aws_db_instance.main.port
}

output "db_name" {
  description = "The database name"
  value       = aws_db_instance.main.db_name
}

output "db_security_group_id" {
  description = "Security Group ID of the RDS database"
  value       = aws_security_group.rds.id
}
