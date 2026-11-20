output "bucket_name" {
  value       = aws_s3_bucket.learning.bucket
  description = "Name of the private learning bucket."
}
output "bucket_arn" {
  value       = aws_s3_bucket.learning.arn
  description = "ARN of the private learning bucket."
}
output "bucket_region" {
  value       = var.aws_region
  description = "AWS Region where the bucket is managed."
}
