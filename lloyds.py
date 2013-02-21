import re
from datetime import date
import urlparse
import requests
import lxml.html
from StringIO import StringIO


def select(xs, key, value):
    for x in xs:
        if x[key] == value:
            return x
    return None


def by_name(xs, value):
    return select(xs, 'name', value)


def dump_headers(headers):
    lines = []
    for name, value in sorted(headers.items()):
        name = name.lower()
        lines.append('  %s: %s' % (name, value))
    return lines


def dump_response(response):
    request = response.request
    lines = ['%s %s %s' % (request.method, response.url, response.status_code)]
    lines.append('Request Headers')
    lines.extend(dump_headers(request.headers))
    if request.method == 'POST':
        lines.append('Form Data: %s' % (request.body,))
    lines.append('Response Headers')
    lines.extend(dump_headers(response.headers))
    lines.append('')
    return '\n'.join(lines)


def print_response(response):
    for r in response.history:
        print dump_response(r)
    print dump_response(response)


def get_login_form(dom, username, password):
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


def submit_form(session, form, allow_redirects=False):
    return session.post(
        form['action'], data=form['params'],
        allow_redirects=allow_redirects)


def fetch_login(username, password, memorable_info):
    base_page = 'https://online.lloydstsb.co.uk/personal/logon/login.jsp'
    session = requests.Session()
    session.headers['pragma'] = 'no-cache'
    session.headers['cache-control'] = 'max-age=0'
    r = session.get(base_page, params={'WT.ac': 'hpIBlogon'})
    form = get_login_form(parse_response(r), username, password)
    # POST /
    form['action'] = urlparse.urljoin(base_page, form['action'])
    t = submit_form(session, form)
    # GET https://secure2.lloydstsb.co.uk/personal/login?mobile=false 302
    t = session.get(t.headers['location'], allow_redirects=False)
    # GET https://secure2.lloydstsb.co.uk/personal/a/logon/entermemorableinformation.jsp

    # XXX: The response from the previous GET sets this cookie to empty,
    # which jml thinks means clearing it.  However, it looks like requests
    # (and/or cookielib) doesn't treat it as such.  If we could get it to
    # handle that, then we could change the POST above to allow redirects and
    # skip much of this crap.
    del session.cookies['redirect']
    location = t.headers['location']
    t = session.get(location, allow_redirects=False)
    form = get_memorable_info(parse_response(t), memorable_info)
    form['action'] = urlparse.urljoin(location, form['action'])
    t = submit_form(session, form, allow_redirects=True)
    # XXX: At this stage, the requests session has the critical IBSESSION
    # cookie from Lloyds.  We're logged in!
    return session, t


_mem_info_re = re.compile('Character (\d+)')
def memorable_info_input(field, mem_info):
    text = field.label.text
    match = _mem_info_re.search(text)
    index = int(match.group(1))
    return '&nbsp;%s' % (mem_info[index - 1],)


def get_memorable_info(dom, mem_info):
    doc = dom.getroot()
    [form] = doc.forms
    data = {}
    for element in form.inputs:
        if getattr(element, 'type', None) == 'image':
            data[element.name + '.x'] = 0
            data[element.name + '.y'] = 0
        elif element.label is not None:
            data[element.name] = memorable_info_input(element, mem_info)
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
        'name': name,
        'balance': balance,
        'url': url,
        }
    account.update(parse_numbers(number))
    return account


def get_accounts(dom, url):
    root = dom.getroot()
    accounts = []
    account_list = root.get_element_by_id('frm1:lstAccLst')
    for li in account_list:
        account = parse_account(li)
        account['url'] = urlparse.urljoin(url, account['url'])
        accounts.append(account)
    return accounts


def get_balances(accounts):
    return dict((a['name'], a['balance']) for a in accounts)


def export_statement_data(session, account, start_date, end_date):
    """Get the statement data for a Lloyds account.

    :param session: A logged-in session.
    :param account: Something identifying the account.
    :param start_date: The start date for the export.
    :param end_date: The end date for the export.
    """
    t = session.get(account['url'])
    dom = parse_response(t)
    url = get_export_link(dom, account)
    t = session.get(url)
    dom = parse_response(t)
    form = _fill_export_form(dom.getroot().forms[0], start_date, end_date)
    form['action'] = urlparse.urljoin(url, form['action'])
    t = submit_form(session, form, allow_redirects=True)
    print t.content
    #t = _submit_export_form(session, form, start_date, end_date)
    #print t.content


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


def parse_response(response):
    # XXX: There _must_ be a better way to do this.  Because the Lloyds pages
    # have pound symbols and smart quotes, the lxml.html parser blows up.
    content = response.text.encode('ascii', 'replace')
    return lxml.html.parse(StringIO(content))


def main():
    # XXX: Credentials should be read from a file or the OS secrets storage.
    session, response = fetch_login('username', 'password', 'memorable-info')
    accounts = get_accounts(parse_response(response), response.url)
    # XXX: Date range should be an input.
    export_statement_data(
        session, by_name(accounts, 'Classic Vantage'),
        date(2013, 2, 1), date.today())


if __name__ == '__main__':
    main()

