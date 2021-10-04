"""
Utility script to continuously read data from a Kinesis stream, from multiple shards, and decode the CloudTrail logs it contains

Sample usage: 
$ python scripts/cat-kinesis.py some-kinesis-stream
"""
import boto3
import sys
import time
import base64
import json

if len(sys.argv) != 2:
    sys.stderr.write("Usage: python scripts/cat-kinesis.py stream-name\n")
    exit(1)

stream_name = sys.argv[1]
kinesis = boto3.client('kinesis')
stream = kinesis.describe_stream(StreamName=stream_name)
shard_ids = [ shard['ShardId'] for shard in stream['StreamDescription']['Shards'] ]
shard_iterators = [ kinesis.get_shard_iterator(StreamName=stream_name, ShardId=shard_id, ShardIteratorType='LATEST')['ShardIterator'] for shard_id in shard_ids]
print(f'Found {len(shard_ids)} shards')
while len(shard_iterators) > 0:
    new_iterators=[]
    for iterator in shard_iterators:
        records = kinesis.get_records(ShardIterator=iterator)
        for record in records.get('Records'):
            print(json.dumps(json.loads(record.get('Data').decode('utf8')), indent=2))
        if records.get('NextShardIterator'):
            new_iterators.append(records.get('NextShardIterator'))
    time.sleep(1)
            
