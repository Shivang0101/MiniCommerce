variable "environment" {
  description = "Deployment environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where ElastiCache will be deployed"
  type        = string
}

variable "private_db_subnet_ids" {
  description = "Subnet IDs for ElastiCache subnet group"
  type        = list(string)
}

variable "app_security_group_id" {
  description = "Security Group ID of application tasks allowed access to Redis"
  type        = string
}

variable "node_type" {
  description = "ElastiCache node instance type"
  type        = string
  default     = "cache.t4g.micro"
}

variable "num_cache_clusters" {
  description = "Number of cache clusters in the replication group"
  type        = number
  default     = 1
}

variable "auth_token" {
  description = "Redis AUTH password token"
  type        = string
  sensitive   = true
}
