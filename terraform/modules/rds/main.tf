# AWS RDS PostgreSQL Module - MiniCommerce Cloud Infrastructure

# DB Subnet Group (Private Database Subnets)
resource "aws_db_subnet_group" "main" {
  name        = "minicommerce-${var.environment}-db-subnet-group"
  subnet_ids  = var.private_db_subnet_ids
  description = "Subnet group for MiniCommerce RDS PostgreSQL"

  tags = {
    Name        = "minicommerce-${var.environment}-db-subnet-group"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# RDS Security Group (Restricts access exclusively from Application Tasks)
resource "aws_security_group" "rds" {
  name        = "minicommerce-${var.environment}-rds-sg"
  description = "Security group restricting access to RDS PostgreSQL"
  vpc_id      = var.vpc_id

  ingress {
    description     = "PostgreSQL access from ECS Application Tasks"
    from_port       = 5432
    to_port         = 5432
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
    Name        = "minicommerce-${var.environment}-rds-sg"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# KMS Key for DB At-Rest Storage Encryption
resource "aws_kms_key" "rds" {
  description             = "KMS key for encrypting MiniCommerce RDS database"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Name        = "minicommerce-${var.environment}-rds-kms"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# RDS PostgreSQL Instance
resource "aws_db_instance" "main" {
  identifier                  = "minicommerce-${var.environment}-postgres"
  engine                      = "postgres"
  engine_version              = "15"
  instance_class              = var.db_instance_class

  allocated_storage           = var.allocated_storage
  max_allocated_storage       = 100
  storage_type                = "gp3"
  storage_encrypted           = true
  kms_key_id                  = aws_kms_key.rds.arn
  db_name                     = var.db_name
  username                    = var.db_username
  password                    = var.db_password
  db_subnet_group_name        = aws_db_subnet_group.main.name
  vpc_security_group_ids      = [aws_security_group.rds.id]
  multi_az                    = var.multi_az
  publicly_accessible         = false
  allow_major_version_upgrade = false
  auto_minor_version_upgrade  = true

  backup_retention_period   = var.environment == "staging" ? 1 : 7
  backup_window             = "03:00-04:00"
  maintenance_window        = "Mon:04:30-Mon:05:30"
  copy_tags_to_snapshot     = true
  skip_final_snapshot       = var.environment == "staging" ? true : false
  final_snapshot_identifier = "minicommerce-${var.environment}-postgres-final-snapshot"

  performance_insights_enabled = var.environment == "staging" ? false : true


  tags = {
    Name        = "minicommerce-${var.environment}-postgres"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
