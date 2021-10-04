import json
import logging
import os
import sys

import telemetry
import transform
from extract import get_cloudtrail_file
from load import write_to_kinesis
from transform import read_cloudtrail_events_file

logger = logging.getLogger()
MAX_CLOUDTRAIL_ENTRIES_PER_KINESIS_RECORD = 100


def setup_logging():
    # https://stackoverflow.com/questions/37703609/using-python-logging-with-aws-lambda
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


def lambda_entrypoint(event, context):
    setup_logging()

    # 1) Read the 'new file' notification sent by S3 and extract the file name
    bucket, path = get_cloudtrail_file(event)

    # 2) Read the CloudTrail log file from the S3 bucket
    cloudtrail_event_payload = read_cloudtrail_events_file(bucket, path)
    cloudtrail_event = json.loads(cloudtrail_event_payload)
    num_events = len(cloudtrail_event.get("Records"))
    logging.info(f'CloudTrail log file has {num_events} log entries')

    # 3) Send to Kinesis
    kinesis_messages = transform.chunk_cloudtrail_events(cloudtrail_event,
                                                         chunk_size=MAX_CLOUDTRAIL_ENTRIES_PER_KINESIS_RECORD)
    kinesis_messages = map(lambda message: json.dumps(message, separators=(',', ':')), kinesis_messages)
    write_to_kinesis(list(kinesis_messages), os.environ['KINESIS_STREAM_NAME'],
                     int(os.environ['KINESIS_STREAM_NUM_SHARDS']))

    # 4) Telemetry
    telemetry.log_event(num_events)


def cli_entrypoint():
    if len(sys.argv) != 4:
        sys.stderr.write("CLI usage: python lambda_handler.py bucket path kinesis-stream")
        exit(1)

    setup_logging()
    _, bucket, path, target_kinesis_stream = sys.argv
    cloudtrail_event_payload = read_cloudtrail_events_file(bucket, path)
    cloudtrail_event = json.loads(cloudtrail_event_payload)
    kinesis_messages = transform.chunk_cloudtrail_events(cloudtrail_event,
                                                         chunk_size=MAX_CLOUDTRAIL_ENTRIES_PER_KINESIS_RECORD)
    kinesis_messages = map(json.dumps, kinesis_messages)
    write_to_kinesis(list(kinesis_messages), target_kinesis_stream)


if __name__ == '__main__':
    cli_entrypoint()
