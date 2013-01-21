from datetime import date
from testtools import TestCase

from .. import amex


class TestAmex(TestCase):

    def test_parse_row(self):
        row = [
            '03/01/2013',
            "Reference: AT130040004000010220720",
            " 32.07",
            "AMAZON EU               AMAZON.CO.UK",
            " Process Date 03/01/2013",
            ]
        data = amex._parse_row(row)
        expected = {
            'date': date(2013, 1, 3),
            'type': 'AMEX',
            'amount': -32.07,
            'description': "AMAZON EU               AMAZON.CO.UK",
            }
        self.assertEqual(expected, data)
