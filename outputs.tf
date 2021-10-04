output "kinesis-stream-name" {
  description = "Name of the newly created Kinesis stream"
  value       = aws_kinesis_stream.cloudtrail-logs.name
}

output "kinesis-stream-arn" {
  description = "ARN of the newly created Kinesis stream"
  value       = aws_kinesis_stream.cloudtrail-logs.arn
}

output "sns-topic-name" {
  description = "Name of the newly creates SNS topic"
  value       = aws_sns_topic.cloudtrail.name
}

output "sns-topic-arn" {
  description = "ARN of the newly creates SNS topic"
  value       = aws_sns_topic.cloudtrail.arn
}