import unittest

import boto3
from moto import mock_kinesis

import load
from tests.utils import get_kinesis_stream_records, nuke_credentials


@mock_kinesis
class TestLoad(unittest.TestCase):
    def setUp(self):
        nuke_credentials()

    def test_writes_to_kinesis(self):
        fake_kinesis = boto3.client('kinesis')
        fake_kinesis.create_stream(StreamName='my-stream', ShardCount=1)

        # Call method
        load.write_to_kinesis(["Never gonna let you down"], 'my-stream')

        # Check that data is properly written to Kinesis
        records = get_kinesis_stream_records('my-stream')
        self.assertEqual(1, len(records))
        self.assertEqual("Never gonna let you down", records[0]['Data'].decode())
