from pprint import pprint
import time
import webbrowser

import gdata.spreadsheet
import gdata.spreadsheet.service
import gdata.spreadsheets.client
import gdata.service


import gdata.gauth

# The client id and secret can be found on your API Console.
CLIENT_ID = '311650427695.apps.googleusercontent.com'
CLIENT_SECRET = '1VPAXyqrf2wBKj8wuLVyG02o'


# Authorization can be requested for multiple APIs at once by specifying multiple scopes separated by # spaces.
SCOPES = ['https://spreadsheets.google.com/feeds/']
USER_AGENT = 'banksucker'

# Save the token for later use.
token = gdata.gauth.OAuth2Token(
   client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scope=' '.join(SCOPES),
   user_agent=USER_AGENT)


url = token.generate_authorize_url()

webbrowser.open(url)
print "Opening", url

time.sleep(1)

code = raw_input('Enter verification code: ').strip()
new_token = token.get_access_token(code)


client = gdata.spreadsheets.client.SpreadsheetsClient(source=USER_AGENT)
client = new_token.authorize(client)

feed = client.get_spreadsheets()

# XXX: Somehow pick the correct spreadsheet
sheet = feed.entry[0]
key = sheet.get_spreadsheet_key()
worksheets = client.get_worksheets(key)
sheet_id = worksheets.CellEntry[0].get_worksheet_id()
# XXX: Great, now we've got the cells, let's do something.
# file:///home/jml/Desktop/gdata-2.0.17/pydocs/gdata.spreadsheets.data.html#CellEntry
cells = client.get_cells(key, sheet_id)
for e in cells.entry:
    print e.content.text

# XXX: Want to add a bunch of rows to the expense spreadsheet

# XXX: For now, hard code the december sheet, but in future, decide on a policy
# for managing them automatically.
# https://developers.google.com/google-apps/documents-list/

# XXX: Do this
# To store the token object in a secured datastore or keystore, the
# gdata.gauth.token_to_blob() function can be used to serialize the token into a
# string. The gdata.gauth.token_from_blob() function does the opposite operation
# and instantiate a new token object from a string.


# XXX: Set up gdata client in virtualenv

#Redirect URIs:  urn:ietf:wg:oauth:2.0:oob
#http://localhost

# https://developers.google.com/google-apps/spreadsheets/
# 