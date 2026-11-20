provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "learning" {
  bucket        = var.bucket_name
  force_destroy = var.force_destroy
  tags = {
    Project     = "aws-usecase-learning-map"
    UseCase     = "UC01"
    Environment = "learning"
    ManagedBy   = "Terraform"
  }
}

resource "aws_s3_bucket_ownership_controls" "learning" {
  bucket = aws_s3_bucket.learning.id
  rule { object_ownership = "BucketOwnerEnforced" }
}

resource "aws_s3_bucket_public_access_block" "learning" {
  bucket                  = aws_s3_bucket.learning.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "learning" {
  bucket = aws_s3_bucket.learning.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "learning" {
  bucket = aws_s3_bucket.learning.id
  rule {
    apply_server_side_encryption_by_default { sse_algorithm = "AES256" }
  }
}

data "aws_iam_policy_document" "deny_insecure_transport" {
  statement {
    sid    = "DenyInsecureTransport"
    effect = "Deny"
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    actions   = ["s3:*"]
    resources = [aws_s3_bucket.learning.arn, "${aws_s3_bucket.learning.arn}/*"]
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
}

resource "aws_s3_bucket_policy" "tls_only" {
  bucket = aws_s3_bucket.learning.id
  policy = data.aws_iam_policy_document.deny_insecure_transport.json
  depends_on = [aws_s3_bucket_public_access_block.learning]
}
