module "cloudtrail-to-kinesis" {
  source                      = "../.."
  cloudtrail-bucket-name      = aws_s3_bucket.cloudtrail.id
  kinesis-stream-name         = "cloudtrail-logs"
  kinesis-retention-time-days = 1
}