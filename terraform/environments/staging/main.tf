# MiniCommerce Staging Environment Terraform Root Configuration

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "MiniCommerce"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# 1. VPC Module
module "vpc" {
  source                   = "../../modules/vpc"
  environment              = var.environment
  vpc_cidr                 = "10.0.0.0/16"
  availability_zones       = ["${var.aws_region}a", "${var.aws_region}b"]
  public_subnet_cidrs      = ["10.0.1.0/24", "10.0.2.0/24"]
  private_app_subnet_cidrs = ["10.0.10.0/24", "10.0.11.0/24"]
  private_db_subnet_cidrs  = ["10.0.20.0/24", "10.0.21.0/24"]
  single_nat_gateway       = true
}

# 2. IAM Roles & Secrets Manager Module
module "iam_and_secrets" {
  source           = "../../modules/iam_and_secrets"
  environment      = var.environment
  db_password      = var.db_password
  redis_auth_token = var.redis_auth_token
  jwt_secret       = var.jwt_secret
}

# 3. Application Load Balancer (ALB) Module
module "alb" {
  source            = "../../modules/alb"
  environment       = var.environment
  vpc_id            = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids
}

# 4. ECS Fargate Cluster & Container Services Module
module "ecs" {
  source                    = "../../modules/ecs"
  environment               = var.environment
  vpc_id                    = module.vpc.vpc_id
  private_app_subnet_ids    = module.vpc.private_app_subnet_ids
  public_subnet_ids         = module.vpc.public_subnet_ids
  alb_security_group_id     = module.alb.alb_security_group_id
  backend_target_group_arn  = module.alb.backend_target_group_arn
  frontend_target_group_arn = module.alb.frontend_target_group_arn
  execution_role_arn        = module.iam_and_secrets.execution_role_arn
  task_role_arn             = module.iam_and_secrets.task_role_arn
  backend_image             = "ghcr.io/shivang0101/minicommerce-backend:latest"
  worker_image              = "ghcr.io/shivang0101/minicommerce-worker:latest"
  frontend_image            = "ghcr.io/shivang0101/minicommerce-frontend:latest"
  db_host                   = module.rds.db_host
  redis_host                = module.elasticache.primary_endpoint_address
  db_password               = var.db_password
  redis_auth_token          = var.redis_auth_token
}

# 5. RDS PostgreSQL Database Module
module "rds" {
  source                = "../../modules/rds"
  environment           = var.environment
  vpc_id                = module.vpc.vpc_id
  private_db_subnet_ids = module.vpc.private_db_subnet_ids
  app_security_group_id = module.ecs.app_security_group_id
  db_name               = "minicommerce"
  db_username           = "postgres"
  db_password           = var.db_password
  db_instance_class     = "db.t4g.micro"
  allocated_storage     = 20
  multi_az              = false
}

# 6. ElastiCache Redis Cluster Module
module "elasticache" {
  source                = "../../modules/elasticache"
  environment           = var.environment
  vpc_id                = module.vpc.vpc_id
  private_db_subnet_ids = module.vpc.private_db_subnet_ids
  app_security_group_id = module.ecs.app_security_group_id
  node_type             = "cache.t4g.micro"
  num_cache_clusters    = 1
  auth_token            = var.redis_auth_token
}
