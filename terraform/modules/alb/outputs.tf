output "alb_dns_name" {
  description = "The DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "alb_arn" {
  description = "The ARN of the Application Load Balancer"
  value       = aws_lb.main.arn
}

output "alb_security_group_id" {
  description = "Security Group ID of the Application Load Balancer"
  value       = aws_security_group.alb.id
}

output "backend_target_group_arn" {
  description = "ARN of the FastAPI Backend target group"
  value       = aws_lb_target_group.backend.arn
}

output "frontend_target_group_arn" {
  description = "ARN of the Nginx Frontend target group"
  value       = aws_lb_target_group.frontend.arn
}
