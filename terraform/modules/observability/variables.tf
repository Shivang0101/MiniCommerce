variable "environment" {
  type        = string
  description = "Deployment environment (e.g. staging, prod)"
  default     = "staging"
}

variable "workspace_alias" {
  type        = string
  description = "Alias name for Amazon Managed Prometheus workspace"
  default     = "minicommerce-prometheus"
}

variable "grafana_name" {
  type        = string
  description = "Name for Amazon Managed Grafana workspace"
  default     = "minicommerce-grafana"
}

variable "enable_grafana" {
  type        = bool
  description = "Enable Amazon Managed Grafana workspace creation (Requires AWS Marketplace Subscription & AWS SSO)"
  default     = false
}

