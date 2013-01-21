from .parser import map_csv, parse_date


def _parse_row(row):
    return {
        'type': 'AMEX',
        'date': parse_date(row[0]),
        'description': row[3],
        'amount': -float(row[2]),
    }


def parse_csv(csv_stream):
    return map_csv(_parse_row, csv_stream, skip_header=False)
