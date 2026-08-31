# AWS Application Load Balancer (ALB) Module - MiniCommerce Cloud Infrastructure

# Security Group for Public ALB
resource "aws_security_group" "alb" {
  name        = "minicommerce-${var.environment}-alb-sg"
  description = "Security group for public Application Load Balancer"
  vpc_id      = var.vpc_id

  ingress {
    description = "Allow inbound HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow inbound HTTPS from internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic to ECS tasks"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "minicommerce-${var.environment}-alb-sg"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "minicommerce-${var.environment}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = var.public_subnet_ids

  enable_deletion_protection = false

  tags = {
    Name        = "minicommerce-${var.environment}-alb"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Target Group: FastAPI Backend (Port 8000)
resource "aws_lb_target_group" "backend" {
  name        = "minicommerce-${var.environment}-tg-backend"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    path                = "/healthz"
    protocol            = "HTTP"
    port                = "8000"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
    matcher             = "200"
  }

  tags = {
    Name        = "minicommerce-${var.environment}-tg-backend"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Target Group: Nginx Frontend (Port 80)
resource "aws_lb_target_group" "frontend" {
  name        = "minicommerce-${var.environment}-tg-frontend"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    path                = "/"
    protocol            = "HTTP"
    port                = "80"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
    matcher             = "200"
  }

  tags = {
    Name        = "minicommerce-${var.environment}-tg-frontend"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Listener: HTTP (Port 80) - Routes API requests to backend and general requests to frontend
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend.arn
  }
}

# Listener Rule: Route /api/* requests to FastAPI Backend Target Group
resource "aws_lb_listener_rule" "api_route" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 10

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }

  condition {
    path_pattern {
      values = ["/api/*", "/docs", "/openapi.json", "/healthz", "/readyz"]
    }
  }
}
