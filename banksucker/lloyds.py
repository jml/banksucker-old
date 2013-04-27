import re
import urlparse
import requests

from .parser import map_csv, parse_date
from .web import submit_form, parse_response


def _get_login_form(dom, username, password):
    doc = dom.getroot()
    [form] = doc.forms
    data = {}
    for element in form.inputs:
        if getattr(element, 'type', None) == 'image':
            data[element.name + '.x'] = 0
            data[element.name + '.y'] = 0
        else:
            data[element.name] = element.value
    data.update(
        {'frmLogin:strCustomerLogin_userID': username,
         'frmLogin:strCustomerLogin_pwd': password})
    return {
        'action': form.action,
        'method': form.method,
        'params': data,
        }


# XXX: No decent errors:
# - wrong user/pass
# - wrong mem info


class Lloyds(object):

    LOGIN_PAGE = 'https://online.lloydstsb.co.uk/personal/logon/login.jsp'

    def __init__(self, token, accounts, url):
        self.token = token
        self.accounts = accounts
        self.url = url

    @classmethod
    def log_in(cls, username, password, memorable_info):
        response = cls._log_in(username, password, memorable_info)
        accounts = get_accounts(parse_response(response), response.url)
        return {
            'token': response.cookies['IBSESSION'],
            'accounts': accounts,
            'url': response.url,
            }

    @classmethod
    def _log_in(cls, username, password, memorable_info):
        session = requests.Session()
        session.headers['pragma'] = 'no-cache'
        session.headers['cache-control'] = 'max-age=0'
        response = session.get(cls.LOGIN_PAGE, params={'WT.ac': 'hpIBlogon'})
        form = _get_login_form(parse_response(response), username, password)
        # POST /
        form['action'] = urlparse.urljoin(cls.LOGIN_PAGE, form['action'])
        response = submit_form(session, form, allow_redirects=False)
        # GET https://secure2.lloydstsb.co.uk/personal/login?mobile=false 302
        response = session.get(response.headers['location'], allow_redirects=False)
        # GET https://secure2.lloydstsb.co.uk/personal/a/logon/entermemorableinformation.jsp

        # XXX: The response from the previous GET sets this cookie to empty,
        # which jml thinks means clearing it.  However, it looks like requests
        # (and/or cookielib) doesn't treat it as such.  If we could get it to
        # handle that, then we could change the POST above to allow redirects and
        # skip much of this crap.
        del session.cookies['redirect']
        location = response.headers['location']
        response = session.get(location, allow_redirects=False)
        # XXX: memorable_info is always lower case.  Maybe this is not the
        # best place to enforce that.
        form = _get_memorable_info(
            parse_response(response), memorable_info.lower())
        form['action'] = urlparse.urljoin(location, form['action'])
        # XXX: At this stage, the requests session has the critical IBSESSION
        # cookie from Lloyds.  We're logged in!
        return submit_form(session, form, allow_redirects=True)

    def get_balances(self):
        return dict((k, v['balance']) for k, v in self.accounts.items())


def _make_session(ib_session):
    session = requests.Session()
    session.cookies['IBSESSION'] = ib_session
    return session


def export_statement_data(ib_session, account, start_date, end_date):
    """Get the statement data for a Lloyds account.

    :param ib_session: The thing returned by `log_in`.
    :param account: Something identifying the account.
    :param start_date: The start date for the export.
    :param end_date: The end date for the export.
    """
    session = _make_session(ib_session)
    t = session.get(account['url'])
    dom = parse_response(t)
    url = get_export_link(dom, account)

    t = session.get(url)
    dom = parse_response(t)
    form = _fill_export_form(dom.getroot().forms[0], start_date, end_date)
    form['action'] = urlparse.urljoin(url, form['action'])
    t = submit_form(session, form, allow_redirects=True)
    return t.content


_mem_info_re = re.compile('Character (\d+)')
def _memorable_info_input(field, mem_info):
    # XXX: Break this up into something that just returns the requested index.
    text = field.label.text
    match = _mem_info_re.search(text)
    index = int(match.group(1))
    return '&nbsp;%s' % (mem_info[index - 1],)


def _get_memorable_info(dom, mem_info):
    doc = dom.getroot()
    [form] = doc.forms
    data = {}
    for element in form.inputs:
        if getattr(element, 'type', None) == 'image':
            data[element.name + '.x'] = 0
            data[element.name + '.y'] = 0
        elif element.label is not None:
            data[element.name] = _memorable_info_input(element, mem_info)
        else:
            data[element.name] = element.value
    return {
        'action': form.action,
        'method': form.method,
        'params': data,
        }


def parse_currency(pounds):
    return float(str(pounds.strip()[1:]).replace(',', ''))


_sort_re = re.compile('\d\d-\d\d-\d\d')

def parse_numbers(number):
    sort, account = number.split(',', 1)
    sort = _sort_re.search(sort).group(0)
    account = account.strip().split()[-1]
    return {'sort-code': sort, 'account-number': account}


def parse_account(li):
    details = li.find_class('accountDetails')[0]
    link = details.iter('a').next()
    name = link.text_content()
    url = link.get('href')
    balance = li.find_class('balance')[0].text_content().split(None, 1)[1]
    balance = parse_currency(balance)
    number = details.find_class('numbers')[0].text_content()
    account = {
        'balance': balance,
        'url': url,
        }
    account.update(parse_numbers(number))
    return name, account


def get_accounts(dom, url):
    root = dom.getroot()
    accounts = {}
    account_list = root.get_element_by_id('frm1:lstAccLst')
    for li in account_list:
        name, account = parse_account(li)
        account['url'] = urlparse.urljoin(url, account['url'])
        accounts[name] = account
    return accounts


def _fill_export_form(form, start_date, end_date):
    data = dict(form.form_values())
    data.update(
        {'frmTest:rdoDateRange': '1',
         'frmTest:dtSearchFromDate': str(start_date.day).zfill(2),
         'frmTest:dtSearchFromDate.month': str(start_date.month).zfill(2),
         'frmTest:dtSearchFromDate.year': str(start_date.year),
         'frmTest:dtSearchToDate': str(end_date.day).zfill(2),
         'frmTest:dtSearchToDate.month': str(end_date.month).zfill(2),
         'frmTest:dtSearchToDate.year': str(end_date.year),
         'frmTest:strExportFormatSelected': 'Internet banking text/spreadsheet (.CSV)',
         'frmTest:btn_Export.x': '0',
         'frmTest:btn_Export.y': '0',
         })
    return {
        'action': form.action,
        'method': form.method,
        'params': data,
        }


def get_export_link(dom, account):
    return urlparse.urljoin(
        account['url'],
        dom.getroot().find_class('export')[0].get('href'))


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
    # XXX: Doesn't seem to work any more with real content.  Check it out.
    return map_csv(_parse_row, csv_stream, skip_header=True)
