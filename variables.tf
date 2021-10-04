variable "cloudtrail-bucket-name" {
  description = "Name of the S3 bucket in which CloudTrail logs are stored (must exist and properly configured to receive CloudTrail logs prior to calling this module)"
  type        = string
}

variable "cloudtrail-sns-topic-name" {
  description = "Name of the SNS topic where information about newly shipped CloudTrail log files are sent"
  type        = string
  default     = "organization-trail-event-notification-topic"
}

variable "kinesis-stream-name" {
  description = "Name of the Kinesis stream used for aggregation"
  type        = string
  default     = "cloudtrail-logs-stream"
}

variable "kinesis-stream-kms-key-id" {
  description = "ID of the KMS key to use for encrypting the Kinesis stream"
  type        = string
  default     = "alias/aws/kinesis"
}

variable "kinesis-num-shards" {
  description = "Number of shards to use in the Kinesis stream"
  type        = number
  default     = 4
}

variable "kinesis-retention-time-days" {
  description = "Retention period of the Kinesis stream (in days)"
  type        = number
  default     = 7
}

variable "lambda-memory" {
  description = "Memory to allocate to the Lambda function"
  type        = number
  default     = 512
}

variable "cloudwatch-logs-retention-time-days" {
  description = "Retention period for the CloudWatch logs of the Lambda function (in days)"
  type        = number
  default     = 7
}