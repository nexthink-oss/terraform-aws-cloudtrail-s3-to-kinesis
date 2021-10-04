# Proxies outputs of the tested module
output "kinesis-stream-name" {
  value = module.cloudtrail.kinesis-stream-name
}

output "kinesis-stream-arn" {
  value = module.cloudtrail.kinesis-stream-arn
}

output "sns-topic-name" {
  value = module.cloudtrail.sns-topic-name
}

output "sns-topic-arn" {
  value = module.cloudtrail.sns-topic-arn
}