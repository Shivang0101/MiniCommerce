variable "environment" {
  type        = string
  description = "Deployment environment name (staging or prod)"
}

variable "alb_arn" {
  type        = string
  description = "ARN of the AWS Application Load Balancer to attach WAF Web ACL"
}
