<<<<<<< HEAD
# S3 Bucket for storing transcripts and weekly reports
resource "aws_s3_bucket" "data_store" {
  bucket = var.s3_bucket_name

  tags = {
    Name        = "Cognora Data Store"
    Project     = "Cognora"
  }
}

# DynamoDB Table for storing analysis scores
resource "aws_dynamodb_table" "scores_table" {
  name           = var.dynamodb_table_name
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "user_id"
  range_key      = "date"

  attribute {
    name = "user_id"
    type = "S"
  }

  attribute {
    name = "date"
    type = "S"
  }

  tags = {
    Name    = "CognoraScores"
    Project = "Cognora"
  }
}

# SNS Topic for sending caregiver alerts
resource "aws_sns_topic" "alert_topic" {
  name = var.sns_topic_name
}

# SNS Email Subscription for the caregiver
resource "aws_sns_topic_subscription" "caregiver_subscription" {
  topic_arn = aws_sns_topic.alert_topic.arn
  protocol  = "email"
  endpoint  = var.caregiver_email
}

# IAM Role for Lambda Function
resource "aws_iam_role" "lambda_exec_role" {
  name = "CognoraLambdaExecRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# IAM Policy attachment for Lambda to access DynamoDB and SNS
resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_dynamodb" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess" # More granular permissions are recommended for production
}

resource "aws_iam_role_policy_attachment" "lambda_sns" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSNSFullAccess" # More granular permissions are recommended for production
}

# Placeholder for Lambda Function
# The actual function code will need to be packaged and uploaded separately.
resource "aws_lambda_function" "alert_lambda" {
  filename      = "lambda_function_payload.zip" # Placeholder
  function_name = "CognoraAlertFunction"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "lambda_handler.handler"
  runtime       = "python3.9"
  source_code_hash = filebase64sha256("lambda_function_payload.zip")

  environment {
    variables = {
      SNS_TOPIC_ARN = aws_sns_topic.alert_topic.arn
      DYNAMODB_TABLE_NAME = var.dynamodb_table_name
    }
  }

  tags = {
    Name    = "CognoraAlertFunction"
    Project = "Cognora"
  }
}
=======
# S3 Bucket for storing transcripts and weekly reports
resource "aws_s3_bucket" "data_store" {
  bucket = var.s3_bucket_name

  tags = {
    Name        = "Cognora Data Store"
    Project     = "Cognora"
  }
}

# DynamoDB Table for storing analysis scores
resource "aws_dynamodb_table" "scores_table" {
  name           = var.dynamodb_table_name
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "user_id"
  range_key      = "date"

  attribute {
    name = "user_id"
    type = "S"
  }

  attribute {
    name = "date"
    type = "S"
  }

  tags = {
    Name    = "CognoraScores"
    Project = "Cognora"
  }
}

# SNS Topic for sending caregiver alerts
resource "aws_sns_topic" "alert_topic" {
  name = var.sns_topic_name
}

# SNS Email Subscription for the caregiver
resource "aws_sns_topic_subscription" "caregiver_subscription" {
  topic_arn = aws_sns_topic.alert_topic.arn
  protocol  = "email"
  endpoint  = var.caregiver_email
}

# IAM Role for Lambda Function
resource "aws_iam_role" "lambda_exec_role" {
  name = "CognoraLambdaExecRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# IAM Policy attachment for Lambda to access DynamoDB and SNS
resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_dynamodb" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess" # More granular permissions are recommended for production
}

resource "aws_iam_role_policy_attachment" "lambda_sns" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSNSFullAccess" # More granular permissions are recommended for production
}

# Placeholder for Lambda Function
# The actual function code will need to be packaged and uploaded separately.
resource "aws_lambda_function" "alert_lambda" {
  filename      = "terraform/lambda_function_payload.zip" # Placeholder
  function_name = "CognoraAlertFunction"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "lambda_handler.handler"
  runtime       = "python3.9"
  source_code_hash = filebase64sha256("terraform/lambda_function_payload.zip") # Placeholder

  environment {
    variables = {
      SNS_TOPIC_ARN = aws_sns_topic.alert_topic.arn
      DYNAMODB_TABLE_NAME = var.dynamodb_table_name
    }
  }

  tags = {
    Name    = "CognoraAlertFunction"
    Project = "Cognora"
  }
}
>>>>>>> 23a3f924b5333426fb4b4fb6085453f9515378f8
