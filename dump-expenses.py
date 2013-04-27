from datetime import date
from pprint import pprint

from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    )
from sqlalchemy.sql import select, and_, func

# XXX: Parametrize dates on the command-line with argparse

# XXX: Store spending plan as data somehow.

# XXX: Synchronize spending plan to Google Drive somehow (or at least make it
# obvious to Joliette).

# XXX: Visualize discrepancies in spending plan.

# XXX: Fix sqlite / SA warnings:
# /home/jml/src/banksucker/.env/local/lib/python2.7/site-packages/sqlalchemy/dialects/sqlite/base.py:791: SAWarning: Did not recognize type 'FLOAT8' of column 'double_val'
#  default, primary_key))


"""
We want to:

 - figure out how much has been "spent" in each account over a given
   period
 - "each account" -> actually a subset of all accounts, specified by name
 - need to handle tree
"""

engine = create_engine(
    'sqlite:////home/jml/Documents/Finance/reboot.gnucash-2013-04-ok')
metadata = MetaData(engine, reflect=True)


splits = Table('splits', metadata, autoload=True)
accounts = Table('accounts', metadata, autoload=True)
transactions = Table('transactions', metadata, autoload=True)


def parse_date(gnucash_date):
    d = gnucash_date
    year, month, day = d[:4], d[4:6], d[6:8]
    return date(int(year), int(month), int(day))


def format_date(date):
    # XXX: zero fill, not space fill.
    return "%s%02d%02d000000" % (date.year, date.month, date.day)


def dump_txns(conn):
    s = splits.alias('s')
    tx = transactions.alias('tx')
    a = accounts.alias('a')
    query = (
        select(
            [s.c.value_num, s.c.value_denom, tx.c.description,
             tx.c.post_date, a.c.name]).
        where(
            and_(
                s.c.tx_guid == tx.c.guid,
                s.c.account_guid == a.c.guid
                )))
    for row in conn.execute(query):
        date = parse_date(row['post_date'])
        value = row['value_num'] / float(row['value_denom'])
        print date, row['name'], row['description'], '%8.02f' % value




def get_spending(conn, start_date, end_date):
    s = splits.alias('s')
    tx = transactions.alias('tx')
    a = accounts.alias('a')

    query = (
        select([a.c.guid, func.sum(s.c.value_num).label('sum'),
                s.c.value_denom.label('denom')]).
        select_from(
            s.join(
                tx, s.c.tx_guid == tx.c.guid).join(
                a, s.c.account_guid == a.c.guid)).
        where(
            and_(
                tx.c.post_date >= format_date(start_date),
                tx.c.post_date < format_date(end_date),
                )).
        group_by(a.c.guid, s.c.value_denom))

    spending = {}
    for row in conn.execute(query):
        spending[row['guid']] = row['sum'] / float(row['denom'])

    names = get_account_names(conn, spending.keys())
    return dict(
        (names[guid], spending[guid]) for guid in spending)


def resolve_account_names(account_guids, parent_map):
    names = {}
    for guid in account_guids:
        current = guid
        while current:
            name, parent = parent_map[current]
            if guid in names:
                names[guid].append(name)
            else:
                names[guid] = [name]
            current = parent
    return dict(
        (guid, ':'.join(reversed(name[:-1])))
        for guid, name in names.items())


def get_account_names(conn, account_guids):
    a = accounts.alias('a')
    # XXX: Number of accounts is always going to be small enough that just
    # querying the lot of them at once is probably faster.
    query = select([a.c.guid, a.c.name, a.c.parent_guid])
    parent_map = {}
    for row in conn.execute(query):
        parent_map[row['guid']] = (row['name'], row['parent_guid'])
    return resolve_account_names(account_guids, parent_map)



if __name__ == '__main__':
    with engine.connect() as conn:
        pprint(get_spending(conn, date(2013, 4, 15), date(2013, 4, 30)))

