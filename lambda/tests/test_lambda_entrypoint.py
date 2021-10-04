import gzip
import json
import os
import unittest

import boto3
from moto import mock_kinesis, mock_s3, mock_cloudwatch

import main as main

# Path of current script
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

from tests.utils import read_test_data, get_kinesis_stream_records, nuke_credentials


@mock_s3
@mock_kinesis
@mock_cloudwatch
class TestLambdaEntryPoint(unittest.TestCase):

    def setUp(self):
        nuke_credentials()
        self.maxDiff = None
        self.fake_kinesis = boto3.client('kinesis')
        self.fake_s3 = boto3.client('s3')

        # Fictious path to where the CloudTrail log file would be on S3
        self.cloudtrail_bucket_name = 'my-cloudtrail-bucket'
        self.cloudtrail_file_name = 'dir/to/cloudtrail.json.gz'

        # Fictious kinesis stream name
        self.kinesis_stream_name = 'mnemonic-cloudtrail-logs'

        # Test file containing an actual gzipped Cloudtrail log file
        self.cloudtrail_file = __location__ + '/data/cloudtrail-log-file.json.gz'

        # Test pre-requisite: S3 bucket with the Cloudtrail log file in it
        self.fake_s3.create_bucket(
            Bucket=self.cloudtrail_bucket_name,
            CreateBucketConfiguration={'LocationConstraint': self.fake_s3.meta.region_name}
        )
        self.fake_s3.upload_file(self.cloudtrail_file, self.cloudtrail_bucket_name, self.cloudtrail_file_name)

        # Test pre-requisite: Kinesis stream
        self.fake_kinesis.create_stream(
            StreamName=self.kinesis_stream_name,
            ShardCount=1
        )

    def tearDown(self):
        self.fake_s3.delete_object(Bucket=self.cloudtrail_bucket_name, Key=self.cloudtrail_file_name)
        self.fake_s3.delete_bucket(Bucket=self.cloudtrail_bucket_name)
        self.fake_kinesis.delete_stream(StreamName=self.kinesis_stream_name)

    def test_entrypoint(self):
        main.os.environ['KINESIS_STREAM_NAME'] = self.kinesis_stream_name
        main.os.environ['KINESIS_STREAM_NUM_SHARDS'] = "1"
        sns_event = read_test_data('sns-event.json')
        # Call Lambda handler
        main.lambda_entrypoint(event=sns_event, context={})

        # Verify if a message was produced
        records = get_kinesis_stream_records(self.kinesis_stream_name)
        self.assertEqual(1, len(records))
        self.assertEqual(18, len(json.loads(records[0].get('Data')).get('Records')))

        # Verify that the Kinesis stream contents matches what we expect
        with gzip.open(self.cloudtrail_file) as f:
            expected_kinesis_contents = f.read().decode('utf-8')
        actual_contents = records[0]['Data'].decode('utf-8')

        self.assertEqual(expected_kinesis_contents, actual_contents)
