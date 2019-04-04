# Requires Google Api Lib
# $ pip3 install --upgrade google-api-python-client
# Requires dateutil
# $ pip3 install --upgrade python-dateutil
# Requires httplib2
# $ pip3 install httplib2

import logging
import os

from apiclient import discovery
import httplib2
import oauth2client
from oauth2client import client
from oauth2client import file
from oauth2client import tools

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = ('https://www.googleapis.com/auth/calendar.readonly',
          'https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/fitness.activity.read')
CREDENTAL_FILE = 'google-api.json'
CLIENT_SECRET_FILE = 'private_data/client_secret.json'
APPLICATION_NAME = 'MonitorMe'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        credentials, the obtained credential.
    """
    # Read the existing credentials
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   CREDENTAL_FILE)
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()

    # If we don't have valid credentials start the oauth flow
    if not credentials or credentials.invalid:
        logging.info('No credentials found. Starting Oauth flow.')
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        logging.info('Storing credentials to ' + credential_path)
    return credentials

def connect_to_api(name, version):
    """Connect to a api encapsulates grabbing credentials and building a service object."""
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build(name, version, http=http)
    return service

# Run get_credientals to get new ones if necessary
if __name__ == '__main__':
    get_credentials()
    connect_to_api('gmail', 'v1')
