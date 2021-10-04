resource "aws_kms_key" "sns-cloudtrail" {
  description         = "KMS key used to encrypt SNS topic containing events of newly delivery CloudTrail log files"
  key_usage           = "ENCRYPT_DECRYPT"
  enable_key_rotation = true
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        # c.f. https://aws.amazon.com/blogs/compute/encrypting-messages-published-to-amazon-sns-with-aws-kms/
        Sid    = "AllowS3ToEncryptMessages"
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        },
        Action   = ["kms:GenerateDataKey*", "kms:Decrypt"],
        Resource = "*"
      },
      {
        # to allow authorized principals to update the key in the future
        Sid    = "DefaultKeyPolicy"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${local.account-id}:root"
        },
        Action   = "kms:*",
        Resource = "*"
      }
    ]
  })
}
