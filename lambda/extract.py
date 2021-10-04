import json


# Extracts the CloudTrail log file name from a SNS notification
# Returns a tuple (bucket, object name)
def get_cloudtrail_file(sns_event: object):
    records = sns_event.get('Records', [])
    if len(records) != 1:
        raise ValueError(f'Expected 1 record, got {len(records)}')

    record = records[0].get('Sns')
    eventName = record.get('Subject')
    if eventName != 'Amazon S3 Notification':
        raise ValueError(f'Ignoring invalid SNS notification type "{eventName}"')

    s3_notification = json.loads(record.get('Message'))
    return _get_cloudtrail_file_from_s3_notification(s3_notification)


# Private method
# Extracts the CloudTrail log file name from a S3 notification
# Returns a tuple (bucket, object name)
def _get_cloudtrail_file_from_s3_notification(s3_notification: object):
    records = s3_notification.get('Records', [])
    if len(records) != 1:
        raise ValueError(f'Expected 1 record, got {len(records)}')

    record = records[0]
    eventName = record.get('eventName')
    if eventName != 'ObjectCreated:Put':
        raise ValueError(f'Ignoring invalid event type "{eventName}"')

    return record['s3']['bucket']['name'], record['s3']['object']['key']
