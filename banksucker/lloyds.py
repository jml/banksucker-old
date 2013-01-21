from __future__ import print_function

import sys

from bs4 import BeautifulSoup
import treq
from twisted.internet.task import react


LOGIN_FORM_URL = 'https://online.lloydstsb.co.uk/personal/logon/login.jsp'
LOGIN_URL = 'https://online.lloydstsb.co.uk/personal/primarylogin'


user_id_field = "frmLogin:strCustomerLogin_userID"
password_field = "frmLogin:strCustomerLogin_pwd"

remember_field = "frmLogin:loginRemember"
'frmLogin:btnLogin1'

hidden_data = {
    'frmLogin': 'frmLogin',
    'submitToken': '',  # Need to get this from login page
    'target': None,
    'hdn_mobile': None,
    }


def chain(d, *callables):
    for function in callables:
        d.addCallback(function)
    return d


def post_done(response):
    return treq.text_content(response)


def parse_form(soup):
    print(soup.form.find_all('input'))


def main(reactor, *args):
    d = treq.get(LOGIN_URL)
    return chain(
        d, post_done, BeautifulSoup,
        parse_form)


react(main, sys.argv)
