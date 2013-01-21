from datetime import date
from StringIO import StringIO

from testtools import TestCase

from .. import lloyds


class TestConversion(TestCase):

    def test_convert(self):
        row = [
            "15/01/2013", "DEB", "30-98-71", "28726568",
            "WWW.ST-DEINIOLS.CO CD 2422", 99.00, None, 4595.66,
            ]
        data = lloyds._parse_row(row)
        self.assertEqual({'date': date(2013, 1, 15),
                          'type': 'DEB',
                          'description': "WWW.ST-DEINIOLS.CO CD 2422",
                          'amount': 99.0}, data)

    def test_parse_file(self):
        stream = StringIO("""\
Transaction Date,Transaction Type,Sort Code,Account Number,Transaction Description,Debit Amount,Credit Amount,Balance,
15/01/2013,DEB,'30-98-71,28726568,WWW.ST-DEINIOLS.CO CD 2422 ,99.00,,4595.66
14/01/2013,DEB,'30-98-71,28726568,CAFFE NERO CD 8921 ,3.10,,4694.66""")
        data = lloyds.parse_csv(stream)
        self.assertEqual(
            [{'date': date(2013, 1, 15),
              'type': 'DEB',
              'description': "WWW.ST-DEINIOLS.CO CD 2422",
              'amount': 99.0},
             {'date': date(2013, 1, 14),
              'type': 'DEB',
              'description': "CAFFE NERO CD 8921",
              'amount': 3.1}], list(data))
