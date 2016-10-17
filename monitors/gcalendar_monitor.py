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
