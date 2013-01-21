import csv

from datetime import datetime


def map_csv(function, csv_stream, skip_header=False):
    reader = csv.reader(csv_stream)
    if skip_header:
        reader.next()
    for row in reader:
        yield function(row)


def parse_date(date_str):
    return datetime.strptime(date_str, '%d/%m/%Y').date()
