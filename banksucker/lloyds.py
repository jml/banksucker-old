from .parser import map_csv, parse_date


def _parse_row(row):
    if row[5] is not None:
        amount = -float(row[5])
    else:
        amount = float(row[6])
    return {
        'date': parse_date(row[0]),
        'type': row[1],
        'description': row[4].strip(),
        'amount': amount,
        }


def parse_csv(csv_stream):
    return map_csv(_parse_row, csv_stream, skip_header=True)
