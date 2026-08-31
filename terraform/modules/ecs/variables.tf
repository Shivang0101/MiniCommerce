variable "environment" {
  description = "Deployment environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where ECS tasks will be deployed"
  type        = string
}

variable "private_app_subnet_ids" {
  description = "List of private application subnet IDs for ECS tasks"
  type        = list(string)
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs for ECS tasks (enables direct ghcr.io image pulling)"
  type        = list(string)
  default     = []
}

variable "alb_security_group_id" {
  description = "Security Group ID of the Application Load Balancer"
  type        = string
}

variable "backend_target_group_arn" {
  description = "Target Group ARN for FastAPI Backend"
  type        = string
}

variable "frontend_target_group_arn" {
  description = "Target Group ARN for Nginx Frontend"
  type        = string
}

variable "execution_role_arn" {
  description = "IAM Task Execution Role ARN"
  type        = string
}

variable "task_role_arn" {
  description = "IAM Task Role ARN"
  type        = string
}

variable "backend_image" {
  description = "Docker image URI for FastAPI Backend"
  type        = string
  default     = "ghcr.io/shivang0101/minicommerce-backend:latest"
}

variable "worker_image" {
  description = "Docker image URI for ARQ Background Worker"
  type        = string
  default     = "ghcr.io/shivang0101/minicommerce-worker:latest"
}

variable "frontend_image" {
  description = "Docker image URI for Nginx Frontend"
  type        = string
  default     = "ghcr.io/shivang0101/minicommerce-frontend:latest"
}

variable "secrets_map" {
  description = "Map of environment variable names to AWS Secrets Manager secret ARNs"
  type        = map(string)
  default     = {}
}

variable "db_host" {
  description = "RDS PostgreSQL host address"
  type        = string
  default     = ""
}

variable "db_name" {
  description = "RDS PostgreSQL database name"
  type        = string
  default     = "minicommerce"
}

variable "db_username" {
  description = "RDS PostgreSQL database user"
  type        = string
  default     = "postgres"
}

variable "redis_host" {
  description = "ElastiCache Redis primary endpoint host"
  type        = string
  default     = ""
}

variable "redis_port" {
  description = "ElastiCache Redis port"
  type        = number
  default     = 6379
}

variable "db_password" {
  description = "RDS PostgreSQL database password"
  type        = string
  sensitive   = true
  default     = ""
}

variable "redis_auth_token" {
  description = "ElastiCache Redis AUTH token"
  type        = string
  sensitive   = true
  default     = ""
}


