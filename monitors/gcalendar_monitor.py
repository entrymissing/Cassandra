import collections
import datetime
import dateutil
import time

from monitors import base_monitor
from monitors import google_api_lib as google_api

class GCalendarQueryMonitor(base_monitor.BaseMonitor):
  def setup(self):
    # Fail with a key error if no query is specified
    self.QUERY = self.config['query']
    self.SUFFIX = self.config['suffix']
    self.NUM_HOURS = self.config.get('num_hours', 7*24)
    self.CALENDAR_NAME = self.config.get('calendar_name', 'Tracking')

  def collect_data(self):
    service = google_api.connect_to_api('calendar', 'v3')
    
    data = []
    now = time.time()
    
    events = google_api.GetCalendarEntriesByQuery(service, self.QUERY,
                                                  self.NUM_HOURS, self.CALENDAR_NAME)
    duration = 0
    for event in events:
      startTs = event['start'].get('dateTime', event['start'].get('date'))
      startTs = dateutil.parser.parse(startTs).timestamp()
      endTs = event['end'].get('dateTime', event['end'].get('date'))
      endTs = dateutil.parser.parse(endTs).timestamp()
      duration += (endTs - startTs)
    
    data.append((self.ts_prefix + '.' + self.SUFFIX + '.count', len(events), now))
    data.append((self.ts_prefix + '.' + self.SUFFIX + '.duration', duration, now))

    return data

class GCalendarTimeSpentAtLocationMonitor(base_monitor.BaseMonitor):
  def setup(self):
    # Fail with a key error if no query is specified
    self.NUM_HOURS = self.config.get('num_hours', 7*24)
    self.CALENDAR_NAME = self.config.get('calendar_name', 'Tracking')
    self.LOCATIONS = self.config.get('locations', ['home', 'work'])

  def collect_data(self):
    service = google_api.connect_to_api('calendar', 'v3')
    
    data = []
    now = time.time()
    ndaysTs = (datetime.datetime.utcnow() - datetime.timedelta(hours = self.NUM_HOURS)).timestamp()
    nowTs = datetime.datetime.utcnow().timestamp()

    events = google_api.GetCalendarEntriesByQuery(service, 'Location',
                                                  self.NUM_HOURS+24*3, self.CALENDAR_NAME)

    locations = collections.defaultdict(int)
    openTrack = False
    for event in events:
      # Get time as timestamp
      curTs = event['start'].get('dateTime', event['start'].get('date'))
      curTs = max(ndaysTs, dateutil.parser.parse(curTs).timestamp())
      curState = event['summary'].split()[-1]
      curLocation = event['summary'].split()[-2]

      if openTrack:
        if curTs > openTs:
          locations[openLocation] += (curTs-openTs)
          openTrack = False
      
      if curState == 'entered':
        openTrack = True
        openTs = curTs
        openLocation = curLocation

      if curState == 'exited':
        openTrack = False
    
    # Add the open remainder if there is any
    if openTrack:
      locations[openLocation] += (nowTs-openTs)
    
    for loc in self.LOCATIONS:
      if loc in locations:
        data.append((self.ts_prefix + '.time_at_7d.' + loc, locations[loc], time.time()))
      else:
        data.append((self.ts_prefix + '.time_at_7d.' + loc, 0, time.time()))

    return data
