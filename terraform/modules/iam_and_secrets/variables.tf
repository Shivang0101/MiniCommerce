variable "environment" {
  description = "Deployment environment name"
  type        = string
}

variable "db_password" {
  description = "PostgreSQL Database master password to store in Secrets Manager"
  type        = string
  sensitive   = true
}

variable "redis_auth_token" {
  description = "Redis AUTH token to store in Secrets Manager"
  type        = string
  sensitive   = true
}

variable "jwt_secret" {
  description = "JWT Secret key to store in Secrets Manager"
  type        = string
  sensitive   = true
}
