resource "aws_iam_role" "lambda-cloudtrail" {
  name        = "lambda-cloudtrail-role"
  description = "Execution role of the Lambda function used to ship CloudTrail logs from a S3 bucket to a Kinesis stream"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = "sts:AssumeRole"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_policy" "lambda-cloudtrail" {
  name        = "lambda-policy"
  path        = "/"
  description = "Role policy of the Lambda function used to ship CloudTrail logs from a S3 bucket to a Kinesis stream"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        # Allow reading from CloudTrail S3 bucket
        Effect   = "Allow",
        Action   = ["s3:GetObject"],
        Resource = "arn:aws:s3:::${var.cloudtrail-bucket-name}/*"
      },
      {
        # Allow writing to Kinesis stream
        Effect   = "Allow",
        Action   = ["kinesis:PutRecord", "kinesis:PutRecords"],
        Resource = aws_kinesis_stream.cloudtrail-logs.arn
      },
      {
        # Allow writing logs and metrics to CloudWatch
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "cloudwatch:PutMetricData"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda-cloudtrail" {
  role       = aws_iam_role.lambda-cloudtrail.name
  policy_arn = aws_iam_policy.lambda-cloudtrail.arn
}

resource "aws_cloudwatch_log_group" "lambda-cloudtrail" {
  name              = "/aws/lambda/${aws_lambda_function.lambda-cloudtrail.function_name}"
  retention_in_days = var.cloudwatch-logs-retention-time-days
}

# Zip lambda source code on the fly
# see https://github.com/hashicorp/terraform/issues/8344
locals {
  lambda-src-path = "${path.module}/lambda"
}
data "archive_file" "lambda-cloudtrail" {
  type        = "zip"
  source_dir  = local.lambda-src-path
  output_path = "lambda.zip"
}

resource "aws_lambda_function" "lambda-cloudtrail" {
  filename         = "lambda.zip"
  source_code_hash = data.archive_file.lambda-cloudtrail.output_base64sha256
  function_name    = "lambda-cloudtrail"
  role             = aws_iam_role.lambda-cloudtrail.arn
  handler          = "main.lambda_entrypoint"
  runtime          = "python3.8" # See https://docs.aws.amazon.com/lambda/latest/dg/API_CreateFunction.html#SSS-CreateFunction-request-Runtime
  timeout          = 900         # seconds
  memory_size      = var.lambda-memory
  tracing_config {
    mode = "Active"
  }

  environment {
    variables = {
      KINESIS_STREAM_NAME       = aws_kinesis_stream.cloudtrail-logs.name
      KINESIS_STREAM_NUM_SHARDS = aws_kinesis_stream.cloudtrail-logs.shard_count
    }
  }
}
