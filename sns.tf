locals {
  cloudtrail_sns_topic_name = "${var.cloudtrail-bucket-name}-event-notification-topic"
  cloudtrail_sqs_queue_name = "${var.cloudtrail-bucket-name}-event-notification-queue"
}

# Bucket notification
resource "aws_s3_bucket_notification" "bucket-notification" {
  bucket = var.cloudtrail-bucket-name

  topic {
    events        = ["s3:ObjectCreated:*"]
    filter_suffix = ".json.gz"
    topic_arn     = aws_sns_topic.cloudtrail.arn
  }
}

# SNS topic
data "aws_iam_policy_document" "sns-topic-policy-document" {
  statement {
    effect    = "Allow"
    actions   = ["SNS:Publish"]
    resources = ["arn:aws:sns:${local.region}:${local.account-id}:${local.cloudtrail_sns_topic_name}"]
    principals {
      type        = "Service"
      identifiers = ["s3.amazonaws.com"]
    }

    condition {
      variable = "aws:SourceArn"
      test     = "ArnLike"
      values   = ["arn:aws:s3:*:*:${var.cloudtrail-bucket-name}"]
    }

    condition {
      variable = "aws:SourceAccount"
      test     = "StringEquals"
      values   = [local.account-id]
    }
  }
}
resource "aws_sns_topic" "cloudtrail" {
  name              = local.cloudtrail_sns_topic_name
  kms_master_key_id = aws_kms_key.sns-cloudtrail.id
  policy            = data.aws_iam_policy_document.sns-topic-policy-document.json
}