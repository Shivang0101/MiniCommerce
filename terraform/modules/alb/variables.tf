variable "environment" {
  description = "Deployment environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where ALB will be deployed"
  type        = string
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs for ALB placement"
  type        = list(string)
}

variable "certificate_arn" {
  description = "ACM Certificate ARN for HTTPS listener (Optional)"
  type        = string
  default     = ""
}
