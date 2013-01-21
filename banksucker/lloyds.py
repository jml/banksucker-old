from __future__ import print_function

import csv
from datetime import datetime


def _parse_row(row):
    return {
        'date': datetime.strptime(row[0], '%d/%m/%Y').date(),
        'type': row[1],
        'description': row[4].strip(),
        'amount': float(row[5]),
        }


def parse_csv(csv_stream):
    reader = csv.reader(csv_stream)
    for row in reader:
        yield _parse_row(row)
