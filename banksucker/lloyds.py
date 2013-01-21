import csv
from datetime import datetime


def _parse_row(row):
    if row[5] is not None:
        amount = -float(row[5])
    else:
        amount = float(row[6])
    return {
        'date': datetime.strptime(row[0], '%d/%m/%Y').date(),
        'type': row[1],
        'description': row[4].strip(),
        'amount': amount,
        }


def parse_csv(csv_stream):
    reader = csv.reader(csv_stream)
    reader.next()
    for row in reader:
        yield _parse_row(row)
