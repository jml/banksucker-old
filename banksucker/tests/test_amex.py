from datetime import date
from StringIO import StringIO
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

    def test_parse_csv(self):
        data = """\
03/01/2013,"Reference: AT130040004000010220720"," 32.07","AMAZON EU               AMAZON.CO.UK"," Process Date 03/01/2013",
03/01/2013,"Reference: AT130040004000010238774"," 11.80","MORPETH ARMS            LONDON"," Process Date 04/01/2013",        
"""
        stream = StringIO(data)
        parsed = amex.parse_csv(stream)
        expected = [
            {'date': date(2013, 1, 3),
             'type': 'AMEX',
             'amount': -32.07,
             'description': "AMAZON EU               AMAZON.CO.UK"},
            {'date': date(2013, 1, 3),
             'type': 'AMEX',
             'description': "MORPETH ARMS            LONDON",
             'amount': -11.8},
        ]
        self.assertEqual(expected, list(parsed))
