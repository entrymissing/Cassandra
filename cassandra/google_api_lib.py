# Requires Google Api Lib
# $ pip3 install --upgrade google-api-python-client
# Requires dateutil
# $ pip3 install --upgrade python-dateutil
# Requires httplib2
# $ pip3 install httplib2

import datetime

from apiclient import errors

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

def GetCalendarEntriesByQuery(service, query, num_hours=7*24, calendar_name='Tracking'):
    # Find the right calendar
    calendar_id = GetCalendarByName(service, calendar_name)

    # Compute some timestamps
    utcnow = datetime.datetime.utcnow()
    ndays = utcnow - datetime.timedelta(hours=num_hours)
    # 'Z' indicates UTC time
    utcnow = utcnow.isoformat() + 'Z'
    ndays = ndays.isoformat() + 'Z'

    events_result = service.events().list(
        calendarId=calendar_id, timeMin=ndays, timeMax=utcnow, q=query, singleEvents=True,
        orderBy='startTime').execute()
    events = events_result.get('items', [])

    return events
