variable "aws_region" {
  description = "AWS Region for the learning bucket."
  type        = string
  default     = "ap-southeast-1"
}

variable "bucket_name" {
  description = "Globally unique S3 bucket name. Use a dedicated learning bucket."
  type        = string
  validation {
    condition     = length(var.bucket_name) >= 3 && length(var.bucket_name) <= 63
    error_message = "bucket_name must contain 3 to 63 characters."
  }
}

variable "force_destroy" {
  description = "Allow Terraform to delete a non-empty learning bucket. Keep false unless intentionally cleaning up test data."
  type        = bool
  default     = false
}
