from bs4 import BeautifulSoup

from datetime import date
from testtools import TestCase

from ..lloyds import parse_form, parse_row


form = """
<form id="frmLogin" name="frmLogin" method="post" action="https://online.lloydstsb.co.uk/personal/primarylogin" class="validationName:(login) validate:()" autocomplete="off" enctype="application/x-www-form-urlencoded">
<div class="inner"><p><strong>Please enter&nbsp;your user ID and password below</strong></p>
<div class="subPanel">
<fieldset>
<div class="formField validate:(required) validationName:(userID) clearfix">
<div class="formFieldInner"><label for="frmLogin:strCustomerLogin_userID">User ID:</label>
<input type="text" autocomplete="off" id="frmLogin:strCustomerLogin_userID" name="frmLogin:strCustomerLogin_userID" class="field setFocus" maxlength="30" value="723869582">
</div>
</div>
<div class="formField validate:(required) validationName:(password) clearfix">
<div class="formFieldInner"><label for="frmLogin:strCustomerLogin_pwd">Password:</label>
<input type="password" id="frmLogin:strCustomerLogin_pwd" name="frmLogin:strCustomerLogin_pwd" class="field" maxlength="20" value=""></div>
</div>
<div class="formField fieldHelp checkbox clearfix">
<div class="formFieldInner"><input id="frmLogin:loginRemember" type="checkbox" name="frmLogin:loginRemember" checked=""> <label for="frmLogin:loginRemember">Remember my User ID</label>
<span class="cxtHelp"> <a class="cxtTrigger" title="Click to find out more about remembering your user ID." href="https://online.lloydstsb.co.uk/personal/logon/login.jsp#cxtHelp1">[?]</a>
</span>
<div id="cxtHelp1" class="help"><h3>Remember my user ID</h3>
<p>Tick this box to save your user ID on this computer. This won't save your password though. You'll still have to enter it each time you want to access your account.</p></div>
</div>
</div>
<div class="inner"><p><strong>Warning:</strong> Don't tick this box if you're using a public or shared computer</p></div>
<div class="loginActions clearfix"><input id="frmLogin:btnLogin1" name="frmLogin:btnLogin1" type="image" class="submitAction" src="./login-form_files/continue-10-1329498072.png" alt="Continue" title="Continue">
<ul id="frmLogin:pnlLogin2" class="linkList">
<li><a id="frmLogin:lkLogin2" name="frmLogin:lkLogin2" href="https://online.lloydstsb.co.uk/personal/a/submitreplaceunlockauthmechanism/customeridentificationdata.jsp" title="Forgotten your password?">Forgotten your password?</a></li>
<li><a id="frmLogin:lkLogin1" name="frmLogin:lkLogin1" href="https://online.lloydstsb.co.uk/personal/a/submitforgottenuserid/forgotUserID.jsp" title="Forgotten your User ID?">Forgotten your User ID?</a></li>
<li><a id="frmLogin:lkLoginTrouble" name="frmLogin:lkLoginTrouble" href="https://online.lloydstsb.co.uk/personal/a/submitreplaceunlockauthmechanism/customeridentificationdata.jsp" title="Having problems logging in?">Having problems logging in?</a></li>
</ul>
</div>
</fieldset>
<input type="hidden" name="frmLogin" value="frmLogin"> <input type="hidden" name="submitToken" value="3839736"> <input type="hidden" name="target" value="">    <input type="hidden" name="hdn_mobile" value="">
</div>
</div>
<input type="hidden" name="hasJS" value="true"></form>
"""


class TestLoginForm(TestCase):

    def test_whatever(self):
        parse_form(BeautifulSoup(form))


class TestConversion(TestCase):

    def test_convert(self):
        row = [
            "15/01/2013", "DEB", "30-98-71", "28726568",
            "WWW.ST-DEINIOLS.CO CD 2422", 99.00, None, 4595.66,
            ]
        data = parse_row(row)
        self.assertEqual({'date': date(2013, 1, 15),
                          'type': 'DEB',
                          'description': "WWW.ST-DEINIOLS.CO CD 2422",
                          'amount': 99.0}, data)
