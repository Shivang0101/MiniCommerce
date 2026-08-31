# AWS VPC Module - MiniCommerce Cloud Infrastructure

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "minicommerce-${var.environment}-vpc"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Internet Gateway for Public Subnets
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name        = "minicommerce-${var.environment}-igw"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Public Subnets (ALB & NAT Gateways)
resource "aws_subnet" "public" {
  count                   = length(var.public_subnet_cidrs)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name        = "minicommerce-${var.environment}-public-subnet-${count.index + 1}"
    Environment = var.environment
    Type        = "Public"
    ManagedBy   = "Terraform"
  }
}

# Private Application Subnets (ECS Fargate Tasks)
resource "aws_subnet" "private_app" {
  count             = length(var.private_app_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_app_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name        = "minicommerce-${var.environment}-private-app-subnet-${count.index + 1}"
    Environment = var.environment
    Type        = "PrivateApp"
    ManagedBy   = "Terraform"
  }
}

# Private Database Subnets (RDS & ElastiCache)
resource "aws_subnet" "private_db" {
  count             = length(var.private_db_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_db_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name        = "minicommerce-${var.environment}-private-db-subnet-${count.index + 1}"
    Environment = var.environment
    Type        = "PrivateDB"
    ManagedBy   = "Terraform"
  }
}

# Elastic IP for NAT Gateway
resource "aws_eip" "nat" {
  count  = var.single_nat_gateway ? 1 : length(var.public_subnet_cidrs)
  domain = "vpc"

  tags = {
    Name        = "minicommerce-${var.environment}-nat-eip-${count.index + 1}"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# NAT Gateway for Outbound Internet Access from Private Subnets
resource "aws_nat_gateway" "main" {
  count         = var.single_nat_gateway ? 1 : length(var.public_subnet_cidrs)
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = {
    Name        = "minicommerce-${var.environment}-nat-gw-${count.index + 1}"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }

  depends_on = [aws_internet_gateway.main]
}

# Public Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name        = "minicommerce-${var.environment}-public-rt"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Public Route Table Associations
resource "aws_route_table_association" "public" {
  count          = length(var.public_subnet_cidrs)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Private App Route Tables
resource "aws_route_table" "private_app" {
  count  = length(var.private_app_subnet_cidrs)
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = var.single_nat_gateway ? aws_nat_gateway.main[0].id : aws_nat_gateway.main[count.index].id
  }

  tags = {
    Name        = "minicommerce-${var.environment}-private-app-rt-${count.index + 1}"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Private App Route Table Associations
resource "aws_route_table_association" "private_app" {
  count          = length(var.private_app_subnet_cidrs)
  subnet_id      = aws_subnet.private_app[count.index].id
  route_table_id = aws_route_table.private_app[count.index].id
}

# Private DB Route Tables (No direct internet routes for database security)
resource "aws_route_table" "private_db" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name        = "minicommerce-${var.environment}-private-db-rt"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Private DB Route Table Associations
resource "aws_route_table_association" "private_db" {
  count          = length(var.private_db_subnet_cidrs)
  subnet_id      = aws_subnet.private_db[count.index].id
  route_table_id = aws_route_table.private_db.id
}
