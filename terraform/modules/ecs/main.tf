# AWS ECS Fargate Cluster & Task Definitions Module - MiniCommerce Cloud Infrastructure

# ECS Fargate Cluster
resource "aws_ecs_cluster" "main" {
  name = "minicommerce-${var.environment}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name        = "minicommerce-${var.environment}-cluster"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Security Group for ECS Fargate Tasks
resource "aws_security_group" "app_tasks" {
  name        = "minicommerce-${var.environment}-app-tasks-sg"
  description = "Security group for ECS Fargate Application Tasks"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Allow HTTP port 8000 from ALB"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [var.alb_security_group_id]
  }

  ingress {
    description     = "Allow HTTP port 80 from ALB"
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [var.alb_security_group_id]
  }

  egress {
    description = "Allow all outbound internet/cloud service traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "minicommerce-${var.environment}-app-tasks-sg"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/minicommerce-${var.environment}-backend"
  retention_in_days = 14

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_cloudwatch_log_group" "worker" {
  name              = "/ecs/minicommerce-${var.environment}-worker"
  retention_in_days = 14

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_cloudwatch_log_group" "frontend" {
  name              = "/ecs/minicommerce-${var.environment}-frontend"
  retention_in_days = 14

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# ==============================================================================
# 1. FASTAPI BACKEND TASK DEFINITION & SERVICE
# ==============================================================================

resource "aws_ecs_task_definition" "backend" {
  family                   = "minicommerce-${var.environment}-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn

  container_definitions = jsonencode([
    {
      name      = "backend"
      image     = var.backend_image
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
          protocol      = "tcp"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.backend.name
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "ecs"
        }
      }
      environment = [
        { name = "ENVIRONMENT", value = var.environment },
        { name = "PORT", value = "8000" },
        { name = "DATABASE_URL", value = "postgresql+asyncpg://${var.db_username}:${var.db_password}@${var.db_host}:5432/${var.db_name}" },
        { name = "REDIS_URL", value = "rediss://:${var.redis_auth_token}@${var.redis_host}:6379/0" }
      ]
    }
  ])

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_ecs_service" "backend" {
  name            = "minicommerce-${var.environment}-backend-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = length(var.public_subnet_ids) > 0 ? var.public_subnet_ids : var.private_app_subnet_ids
    security_groups  = [aws_security_group.app_tasks.id]
    assign_public_ip = length(var.public_subnet_ids) > 0 ? true : false
  }

  load_balancer {
    target_group_arn = var.backend_target_group_arn
    container_name   = "backend"
    container_port   = 8000
  }

  depends_on = [var.backend_target_group_arn]
}

# Auto Scaling for FastAPI Backend
resource "aws_appautoscaling_target" "backend" {
  max_capacity       = 4
  min_capacity       = 1
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.backend.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "backend_cpu" {
  name               = "minicommerce-${var.environment}-backend-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.backend.resource_id
  scalable_dimension = aws_appautoscaling_target.backend.scalable_dimension
  service_namespace  = aws_appautoscaling_target.backend.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 70.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

# ==============================================================================
# 2. ARQ BACKGROUND WORKER TASK DEFINITION & SERVICE (0 open HTTP ports)
# ==============================================================================

resource "aws_ecs_task_definition" "worker" {
  family                   = "minicommerce-${var.environment}-worker"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn

  container_definitions = jsonencode([
    {
      name      = "worker"
      image     = var.worker_image
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.worker.name
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "ecs"
        }
      }
      environment = [
        { name = "ENVIRONMENT", value = var.environment },
        { name = "DATABASE_URL", value = "postgresql+asyncpg://${var.db_username}:${var.db_password}@${var.db_host}:5432/${var.db_name}" },
        { name = "REDIS_URL", value = "rediss://:${var.redis_auth_token}@${var.redis_host}:6379/0" }
      ]
    }
  ])

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_ecs_service" "worker" {
  name            = "minicommerce-${var.environment}-worker-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.worker.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = length(var.public_subnet_ids) > 0 ? var.public_subnet_ids : var.private_app_subnet_ids
    security_groups  = [aws_security_group.app_tasks.id]
    assign_public_ip = length(var.public_subnet_ids) > 0 ? true : false
  }
}

# ==============================================================================
# 3. NGINX FRONTEND TASK DEFINITION & SERVICE
# ==============================================================================

resource "aws_ecs_task_definition" "frontend" {
  family                   = "minicommerce-${var.environment}-frontend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn

  container_definitions = jsonencode([
    {
      name      = "frontend"
      image     = var.frontend_image
      essential = true
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
          protocol      = "tcp"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.frontend.name
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_ecs_service" "frontend" {
  name            = "minicommerce-${var.environment}-frontend-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.frontend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = length(var.public_subnet_ids) > 0 ? var.public_subnet_ids : var.private_app_subnet_ids
    security_groups  = [aws_security_group.app_tasks.id]
    assign_public_ip = length(var.public_subnet_ids) > 0 ? true : false
  }

  load_balancer {
    target_group_arn = var.frontend_target_group_arn
    container_name   = "frontend"
    container_port   = 80
  }

  depends_on = [var.frontend_target_group_arn]
}
