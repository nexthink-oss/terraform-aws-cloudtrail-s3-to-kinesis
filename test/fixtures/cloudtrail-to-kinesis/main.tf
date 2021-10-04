provider "aws" {
  region = var.region
}

resource "aws_s3_bucket" "cloudtrail" {
  bucket        = var.cloudtrail-bucket-name
  acl           = "private"
  force_destroy = true
}

module "cloudtrail" {
  source                 = "../../.."
  cloudtrail-bucket-name = aws_s3_bucket.cloudtrail.id
  kinesis-stream-name    = var.kinesis-stream-name
  kinesis-num-shards     = 1
}
