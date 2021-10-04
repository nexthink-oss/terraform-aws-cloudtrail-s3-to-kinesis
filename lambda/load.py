import logging
import random
from typing import List

import boto3

# https://docs.aws.amazon.com/kinesis/latest/APIReference/API_PutRecords.html
KINESIS_MAX_NUM_RECORDS = 500
KINESIS_MAX_RECORDS_PER_BATCH = 10


def write_to_kinesis(payload: List[str], stream_name: str, num_shards: int = 1):
    kinesis = boto3.client('kinesis')

    # Write at most KINESIS_MAX_RECORDS_PER_BATCH records at a time
    batches = [payload[i:i + KINESIS_MAX_RECORDS_PER_BATCH] for i in
               range(0, len(payload), KINESIS_MAX_RECORDS_PER_BATCH)]
    logging.info(f'Writing CloudTrail log payload to Kinesis ({len(payload)} records in {len(batches)} batches)')
    for batch in batches:
        result = kinesis.put_records(
            StreamName=stream_name,
            Records=[{'Data': message, 'PartitionKey': str(random.randint(1, num_shards))} for message in batch],
        )
    logging.info(f'Successfully shipped {len(payload)} records to Kinesis')
