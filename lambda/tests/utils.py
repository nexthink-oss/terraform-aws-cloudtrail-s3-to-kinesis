import json
import os

import boto3

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def read_test_data(name):
    with open(os.path.join(__location__, 'data', name), 'r') as f:
        return json.loads(f.read())


def get_kinesis_stream_records(stream_name):
    fake_kinesis = boto3.client('kinesis')
    stream = fake_kinesis.describe_stream(StreamName=stream_name)
    shard_iterator = fake_kinesis.get_shard_iterator(
        StreamName=stream_name,
        ShardId=stream['StreamDescription']['Shards'][0]['ShardId'],
        ShardIteratorType='TRIM_HORIZON'
    )['ShardIterator']

    return fake_kinesis.get_records(ShardIterator=shard_iterator, Limit=100).get('Records')


def nuke_credentials():
    # Ensure we don't hit an actual AWS account
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
