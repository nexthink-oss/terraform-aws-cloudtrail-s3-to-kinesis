# Lambda function to ship CloudTrail log files to Kinesis

This Lambda function receives as an input
a [S3 bucket notification](https://docs.aws.amazon.com/AmazonS3/latest/userguide/NotificationHowTo.html) (see
a [sample](./tests/data/s3-notification.json) one) indicating that AWS has delivered a new CloudTrail log file. The
Lambda function then reads this file from S3 and writes it to a Kinesis stream.

## Installation

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r test-requirements.txt # If you plan to run tests
```

## Running manually

The code can be run manually from the CLI using:

```
python main.py <cloudtrail-bucket-name> <cloudtrail-log-file> <kinesis-stream>
```

for instance:

```
python main.py nxt-organization-trail 'organization-trail/AWSLogs/o-xxxxx/987654321098/CloudTrail/eu-west-1/2021/04/09/987654321098_CloudTrail_eu-west-1_20210409T0000Z_EmJC82ZLOa1iL758.json.gz' my-kinesis-stream
```

In which case it will ship the CloudTrail log file to Kinesis.

## Code structure

- `main.py` contains the Lambda and CLI entrypoints
- `extract.py` contains the logic that parses the Lambda input
- `transform.py` contains the processing logic
- `load.py` contains the logic writing data to Kinesis

## Unit tests

Unit tests do not use a real AWS account. They only use [moto](https://github.com/spulec/moto) to mock the AWS API
client. Run using:

```
$ make test
```
