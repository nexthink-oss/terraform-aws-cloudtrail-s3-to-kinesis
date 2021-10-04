# Complete example

This examples creates:
- A S3 bucket to store CloudTrail logs
- A regional CloudTrail trail deliverying logs to the above S3 bucket
- The necessary infrastructure to ship CloudTrail logs from S3 to Kinesis using the `terraform-aws-cloudtrail-s3-to-kinesis` module

## Usage 

- Initialize and apply the Terraform configuration:

```
terraform init
terraform apply
```

- Run: 

```
python3 ../../scripts/cat-kinesis.py cloudtrail-logs
```

- Wait for around 15-25 minutes to give the CloudTrail delivery service time to ship CloudTrail logs to your newly created S3 bucket. Then, you will see CloudTrail logs being read from Kinesis.