variable "environment" {
  description = "Deployment environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where RDS will be deployed"
  type        = string
}

variable "private_db_subnet_ids" {
  description = "Subnet IDs for the RDS DB subnet group"
  type        = list(string)
}

variable "app_security_group_id" {
  description = "Security Group ID of the application tasks allowed to access RDS"
  type        = string
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "minicommerce"
}

variable "db_username" {
  description = "Master database username"
  type        = string
  default     = "postgres"
}

variable "db_password" {
  description = "Master database password"
  type        = string
  sensitive   = true
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.micro"
}

variable "allocated_storage" {
  description = "Allocated storage size in GB"
  type        = number
  default     = 20
}

variable "multi_az" {
  description = "Enable Multi-AZ deployment for high availability"
  type        = bool
  default     = false
}
