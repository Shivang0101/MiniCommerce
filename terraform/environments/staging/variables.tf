variable "aws_region" {
  description = "AWS Region to deploy resources into"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "staging"
}

variable "db_password" {
  description = "PostgreSQL Master Password"
  type        = string
  sensitive   = true
  default     = "StagingSecurePass123!"
}

variable "redis_auth_token" {
  description = "Redis AUTH Password"
  type        = string
  sensitive   = true
  default     = "StagingRedisSecretKey99!"
}

variable "jwt_secret" {
  description = "JWT Secret Key"
  type        = string
  sensitive   = true
  default     = "SuperSecretStagingJWTKey2026!"
}
