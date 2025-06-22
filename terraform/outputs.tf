output "s3_bucket_id" {
  description = "The ID of the S3 bucket."
  value       = aws_s3_bucket.data_store.id
}

output "dynamodb_table_name" {
  description = "The name of the DynamoDB table."
  value       = aws_dynamodb_table.scores_table.name
}

output "sns_topic_arn" {
  description = "The ARN of the SNS topic for alerts."
  value       = aws_sns_topic.alert_topic.arn
}

output "lambda_function_name" {
  description = "The name of the Lambda function."
  value       = aws_lambda_function.alert_lambda.function_name
}
