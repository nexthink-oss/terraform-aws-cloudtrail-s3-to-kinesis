from datetime import datetime

import boto3

METRIC_NAME = 'NumberOfCloudTrailRecordsShippedToKinesis'
METRIC_NAMESPACE = 'CloudtrailS3ToKinesisShipper'


def log_event(num_cloudtrail_records: int):
    cloudwatch = boto3.client('cloudwatch')
    metric_data = [{
        'MetricName': METRIC_NAME,
        'Dimensions': [],
        'Timestamp': datetime.now(),
        'Value': num_cloudtrail_records,
        'Unit': 'Count'
    }]
    cloudwatch.put_metric_data(Namespace=METRIC_NAMESPACE, MetricData=metric_data)
