resource "aws_wafv2_web_acl" "main" {
  name        = "minicommerce-${var.environment}-waf"
  description = "AWS WAF Web ACL protecting Application Load Balancer from SQLi, XSS, and rate limit abuse"
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  # Rule 1: Custom Rate Limiting (Block IPs exceeding 1,000 requests per 5 minutes)
  rule {
    name     = "RateLimitRule"
    priority = 10

    action {
      block {}
    }

    statement {
      rate_based_statement {
        limit              = 1000
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "minicommerce-${var.environment}-rate-limit"
      sampled_requests_enabled   = true
    }
  }

  # Rule 2: AWS Managed Rules Common Rule Set (SQLi, XSS, General Protection)
  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 20

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "minicommerce-${var.environment}-common-rules"
      sampled_requests_enabled   = true
    }
  }

  # Rule 3: AWS Managed Rules Known Bad Inputs Rule Set
  rule {
    name     = "AWSManagedRulesKnownBadInputsRuleSet"
    priority = 30

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "minicommerce-${var.environment}-bad-inputs"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "minicommerce-${var.environment}-waf-acl"
    sampled_requests_enabled   = true
  }

  tags = {
    Name        = "minicommerce-${var.environment}-waf"
    Environment = var.environment
  }
}

# Attach WAF Web ACL to AWS Application Load Balancer
resource "aws_wafv2_web_acl_association" "alb_assoc" {
  resource_arn = var.alb_arn
  web_acl_arn  = aws_wafv2_web_acl.main.arn
}
