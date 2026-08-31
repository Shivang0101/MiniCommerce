# MiniCommerce V7: AWS Cloud Architecture & Infrastructure as Code (IaC)

## Executive Summary
Version 7 introduces an enterprise-grade, multi-AZ cloud architecture on Amazon Web Services (AWS) fully provisioned using **Terraform**. This eliminates manual cloud configuration, guarantees 100% reproducible staging and production environments, and ensures zero downtime with auto-scaling container services.

---

## 🏗️ AWS Cloud Topology Diagram

```
                                  PUBLIC INTERNET
                                         │
                                         ▼
                     +---------------------------------------+
                     |   AWS Application Load Balancer (ALB) |
                     |   Public Subnets (AZ-1 & AZ-2)        |
                     +---------------------------------------+
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 │ Path: /api/*, /docs, /healthz                 │ Path: /*
                 ▼                                               ▼
   +---------------------------+                   +---------------------------+
   | FastAPI Backend Container |                   | Nginx Frontend Container  |
   | Private App Subnets       |                   | Private App Subnets       |
   +---------------------------+                   +---------------------------+
                 │                                               │
                 ├───────────────────────┐                       │
                 ▼                       ▼                       │
   +---------------------------+   +---------------------------+ │
   | PostgreSQL 15 (RDS)       |   | Redis 7 (ElastiCache)     | │
   | Private DB Subnets        |   | Private DB Subnets        | │
   +---------------------------+   +---------------------------+ │
                                         ▲                       │
                                         │                       │
                                   +---------------------------+ │
                                   | ARQ Background Worker     |◄┘
                                   | Private App Subnets (0 HTTP)|
                                   +---------------------------+
```

---

## 📦 Terraform Module Directory Breakdown

```
terraform/
├── environments/
│   ├── staging/
│   │   ├── main.tf                 # Staging provider and module instantiations
│   │   ├── variables.tf            # Staging input variables
│   │   ├── outputs.tf              # ALB DNS, RDS & Redis endpoint outputs
│   │   └── terraform.tfvars.example # Example variable values
│   └── prod/                       # Production environment configuration
└── modules/
    ├── vpc/                        # VPC, Public/Private Subnets, NAT Gateways
    ├── rds/                        # RDS PostgreSQL 15 Multi-AZ & KMS Encryption
    ├── elasticache/                # ElastiCache Redis Replication Group & TLS
    ├── alb/                        # Application Load Balancer, Target Groups & Rules
    ├── ecs/                        # ECS Fargate Cluster, Task Defs & Auto-Scaling
    └── iam_and_secrets/            # IAM Execution/Task Roles & Secrets Manager
```

---

## 🛠️ Step-by-Step Deployment Runbook

### 1. Prerequisites Verification
Ensure Terraform CLI (`>= 1.5.0`) and AWS CLI v2 are installed and configured:
```powershell
aws --version
terraform -v
aws configure
```

### 2. Local Code Validation (0 AWS Cost)
Navigate to the staging environment directory and initialize/validate the Terraform configuration:
```powershell
cd terraform/environments/staging
terraform init
terraform validate
terraform fmt -check -recursive ../..
```

### 3. Dry-Run Execution Plan
Calculate the execution graph showing all resources that will be provisioned:
```powershell
terraform plan
```

### 4. Cloud Resource Provisioning
Apply the Terraform execution plan to create live AWS resources:
```powershell
terraform apply -auto-approve
```

### 5. Infrastructure Teardown (Cost Protection)
When testing or demonstration is complete, destroy all cloud resources to prevent idle charges:
```powershell
terraform destroy -auto-approve
```

---

## 🔐 Security & Cost Optimization Principles

1. **Private Subnet Isolation**: Neither PostgreSQL nor Redis is accessible from the public internet. Access is strictly restricted to ECS task security groups on ports 5432 and 6379.
2. **Secrets Manager Integration**: Database passwords, Redis AUTH tokens, and JWT secret keys are stored encrypted in AWS Secrets Manager and dynamically injected into containers at startup.
3. **Single NAT Gateway Option**: Staging uses a single shared NAT Gateway to minimize hourly AWS VPC charges.
