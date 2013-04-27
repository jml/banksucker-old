"""Generic web scraping stuff."""

import lxml.html
from StringIO import StringIO


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


def submit_form(session, form, allow_redirects=False):
    return session.post(
        form['action'], data=form['params'],
        allow_redirects=allow_redirects)


def parse_response(response):
    # XXX: There _must_ be a better way to do this.  Because the Lloyds pages
    # have pound symbols and smart quotes, the lxml.html parser blows up.
    content = response.text.encode('ascii', 'replace')
    return lxml.html.parse(StringIO(content))
