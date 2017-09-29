# Requires Google Api Lib
# $ pip3 install --upgrade google-api-python-client
# Requires dateutil
# $ pip3 install --upgrade python-dateutil

import datetime
import httplib2
import os

from apiclient import discovery
from apiclient import errors
import oauth2client
from oauth2client import client
from oauth2client import tools

import dateutil.parser

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = ('https://www.googleapis.com/auth/calendar.readonly',
          'https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/fitness.activity.read')
CLIENT_SECRET_FILE = 'private_data/client_secret.json'
APPLICATION_NAME = 'MonitorMe'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
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
      flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
      flow.user_agent = APPLICATION_NAME
      credentials = tools.run_flow(flow, store)
      print('Storing credentials to ' + credential_path)
    return credentials

# Run get_credientals to get new ones if necessary
if __name__ == '__main__':
  get_credentials()

def connect_to_api(name, version):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build(name, version, http=http)
    return service

def ListMessagesMatchingQuery(service, query='', user_id='me'):
  """List all Messages of the user's mailbox matching the query.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    query: String used to filter messages returned.
    Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

  Returns:
    List of Messages that match the criteria of the query. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate ID to get the details of a Message.
  """
  try:
    response = service.users().messages().list(userId=user_id,
                                               q=query).execute()
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id, q=query,
                                         pageToken=page_token).execute()
      messages.extend(response['messages'])
    return messages
  except errors.HttpError as error:
    print('An error occurred: %s' % error)
    return []

def GetMessage(service, user_id, msg_id):
  """Get a Message with given ID.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    A Message.
  """
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()
    return message
  except errors.HttpError as error:
    print('An error occurred: %s' % error)

def GetCalendarByName(service, name):
  page_token = None
  while True:
    calendar_list = service.calendarList().list(pageToken=page_token).execute()
    for calendar_list_entry in calendar_list['items']:
      if calendar_list_entry['summary'] == name:
        return calendar_list_entry['id']
    page_token = calendar_list.get('nextPageToken')
    if not page_token:
      break
  return None

def GetCalendarEntriesByQuery(service, query, num_hours = 7*24, calendar_name = 'Tracking'):
  # Find the right calendar
  calendar_id = GetCalendarByName(service, calendar_name)

  # Compute some timestamps
  utcnow = datetime.datetime.utcnow()
  ndays = utcnow - datetime.timedelta(hours = num_hours)
  # 'Z' indicates UTC time
  utcnow = utcnow.isoformat() + 'Z'
  ndays = ndays.isoformat() + 'Z'

  eventsResult = service.events().list(
      calendarId=calendar_id, timeMin=ndays, timeMax=utcnow, q=query, singleEvents=True,
      orderBy='startTime').execute()
  events = eventsResult.get('items', [])
  
  return events
