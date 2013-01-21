import csv
from datetime import datetime


def _parse_row(row):
    return {
        'type': 'AMEX',
        'date': datetime.strptime(row[0], '%d/%m/%Y').date(),
        'description': row[3],
        'amount': -float(row[2]),
    }


def parse_csv(csv_stream):
    reader = csv.reader(csv_stream)
    for row in reader:
        yield _parse_row(row)
