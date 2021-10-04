import unittest

import extract
from tests.utils import read_test_data


class TestExtract(unittest.TestCase):
    def setUp(self):
        pass

    def test_extract(self):
        sns_event = read_test_data('sns-event.json')
        bucket, path = extract.get_cloudtrail_file(sns_event)

        self.assertEqual('my-cloudtrail-bucket', bucket)
        self.assertEqual('dir/to/cloudtrail.json.gz', path)
