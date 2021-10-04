import gzip
import unittest

import boto3
from moto import mock_s3

import transform
from tests.utils import nuke_credentials


@mock_s3
class TestExtract(unittest.TestCase):
    def setUp(self):
        nuke_credentials()

    def test_returns_correct_data_from_s3(self):
        fake_s3 = boto3.client('s3')

        # Set up: Mock bucket and CloudTrail log file
        fake_s3.create_bucket(Bucket='my-bucket',
                              CreateBucketConfiguration={'LocationConstraint': fake_s3.meta.region_name})

        boto3.resource('s3').Object('my-bucket', '/path/to/cloudtrail-file.json.gz').put(
            Body=gzip.compress("Never gonna give you up".encode("utf-8")))

        # Test that the method will read the data from S3 and properly return it
        result = transform.read_cloudtrail_events_file('my-bucket', '/path/to/cloudtrail-file.json.gz')
        self.assertEqual("Never gonna give you up", result.decode())

    def test_chunking(self):
        sample_events = {'Records': ["hello" for i in range(42)]}
        chunks = transform.chunk_cloudtrail_events(sample_events, chunk_size=50)
        self.assertEqual(1, len(chunks))
        self.assertEqual(sample_events, chunks[0])

        sample_events = {'Records': ["hello" for i in range(201)]}
        chunks = transform.chunk_cloudtrail_events(sample_events, chunk_size=100)
        self.assertEqual(3, len(chunks))
        self.assertEqual(100, len(chunks[0]['Records']))
        self.assertEqual(100, len(chunks[1]['Records']))
        self.assertEqual(1, len(chunks[2]['Records']))
