# AWS ElastiCache Redis Module - MiniCommerce Cloud Infrastructure

# ElastiCache Subnet Group (Private Database Subnets)
resource "aws_elasticache_subnet_group" "main" {
  name       = "minicommerce-${var.environment}-redis-subnet-group"
  subnet_ids = var.private_db_subnet_ids

  tags = {
    Name        = "minicommerce-${var.environment}-redis-subnet-group"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# ElastiCache Security Group (Restricts access exclusively from Application Tasks)
resource "aws_security_group" "redis" {
  name        = "minicommerce-${var.environment}-redis-sg"
  description = "Security group restricting access to ElastiCache Redis"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Redis port 6379 from ECS Application Tasks"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [var.app_security_group_id]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "minicommerce-${var.environment}-redis-sg"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Parameter Group
resource "aws_elasticache_parameter_group" "main" {
  name   = "minicommerce-${var.environment}-redis7-params"
  family = "redis7"

  parameter {
    name  = "maxmemory-policy"
    value = "volatile-lru"
  }
}

# Redis Replication Group
resource "aws_elasticache_replication_group" "main" {
  replication_group_id = "minicommerce-${var.environment}-redis"
  description          = "Redis replication cluster for MiniCommerce cache and ARQ background worker tasks"
  node_type            = var.node_type
  num_cache_clusters   = var.num_cache_clusters
  port                 = 6379
  parameter_group_name = aws_elasticache_parameter_group.main.name
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.redis.id]

  apply_immediately          = true
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token                 = var.auth_token

  automatic_failover_enabled = var.num_cache_clusters > 1 ? true : false

  tags = {
    Name        = "minicommerce-${var.environment}-redis"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
