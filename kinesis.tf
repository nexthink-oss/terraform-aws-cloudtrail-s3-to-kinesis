resource "aws_kinesis_stream" "cloudtrail-logs" {
  name             = var.kinesis-stream-name
  shard_count      = var.kinesis-num-shards
  retention_period = var.kinesis-retention-time-days * 24
  encryption_type  = "KMS"
  kms_key_id       = var.kinesis-stream-kms-key-id
}