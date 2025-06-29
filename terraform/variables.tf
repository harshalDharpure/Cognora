<<<<<<< HEAD
variable "aws_region" {
  description = "The AWS region to create resources in."
  type        = string
  default     = "us-east-1"
}

variable "s3_bucket_name" {
  description = "The name of the S3 bucket for storing transcripts and reports."
  type        = string
  default     = "cognora-data-store-harshal-9922"
}

variable "dynamodb_table_name" {
  description = "The name of the DynamoDB table for storing scores."
  type        = string
  default     = "CognoraScores"
}

variable "sns_topic_name" {
  description = "The name of the SNS topic for caregiver alerts."
  type        = string
  default     = "CognoraAlerts"
}

variable "caregiver_email" {
  description = "The email address to subscribe to the SNS topic for alerts."
  type        = string
}
=======
variable "aws_region" {
  description = "The AWS region to create resources in."
  type        = string
  default     = "us-east-1"
}

variable "s3_bucket_name" {
  description = "The name of the S3 bucket for storing transcripts and reports."
  type        = string
  default     = "cognora-data-store"
}

variable "dynamodb_table_name" {
  description = "The name of the DynamoDB table for storing scores."
  type        = string
  default     = "CognoraScores"
}

variable "sns_topic_name" {
  description = "The name of the SNS topic for caregiver alerts."
  type        = string
  default     = "CognoraAlerts"
}

variable "caregiver_email" {
  description = "The email address to subscribe to the SNS topic for alerts."
  type        = string
}
>>>>>>> 23a3f924b5333426fb4b4fb6085453f9515378f8
