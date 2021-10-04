import gzip
import logging
from typing import List

import boto3


def read_cloudtrail_events_file(bucket: str, path: str):
    s3 = boto3.resource('s3')
    logging.info(f'Reading CloudTrail log file s3://{bucket}/{path}')
    raw_bytes = s3.Object(bucket, path).get()['Body'].read()
    return gzip.decompress(raw_bytes)


def chunk_cloudtrail_events(cloudtrail_event: object, chunk_size) -> List[object]:
    records = cloudtrail_event.get('Records')
    record_chunks = [records[i:i + chunk_size] for i in range(0, len(records), chunk_size)]
    logging.info(f'Chunked CloudTrail records in {len(record_chunks)} chunks')
    return [{'Records': record_chunk} for record_chunk in record_chunks]
