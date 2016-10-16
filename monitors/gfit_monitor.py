import datetime
import time

from monitors import base_monitor
from monitors import google_api_lib as google_api

class GFitMonitor(base_monitor.BaseMonitor):
  def setup(self):
    # Queries and suffixes
    self.TIME_WINDOWS = self.config.get('time_windows', [24*7])
    self.SUFFIXES = self.config.get('suffixes', ['7d'])
    
    # Assert that both are the same length
    if not len(self.TIME_WINDOWS) == len(self.SUFFIXES):
      raise KeyError('Queries %s and Suffixes %s are not the same length' %
          (self.TIME_WINDOWS, self.SUFFIXES))

  def collect_data(self):
    service = google_api.connect_to_api('fitness', 'v1')
    data = []
    now = time.time()
    utcnow = datetime.datetime.utcnow()
    
    for hours, suffix in zip(self.TIME_WINDOWS, self.SUFFIXES):
      ndays = utcnow - datetime.timedelta(hours = hours)
      startTime = ndays.isoformat("T") + "Z"
      response = service.users().sessions().list(userId='me', startTime=startTime).execute()

      numWorkout = len(response['session'])
      timeWorkout = 0
      for s in response['session']:
        timeWorkout += ((int(s['endTimeMillis'])-int(s['startTimeMillis'])) / 1000)
      
      data.append((self.ts_prefix + '.num_workout.' + suffix, numWorkout, now))
      data.append((self.ts_prefix + '.time_workout.' + suffix, timeWorkout, now))
    return data
