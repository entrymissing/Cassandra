import time

import datetime

from cassandra.probes import base_prober
from cassandra import google_api_credentials_lib as google_creds

__PROBE_NAME = ['GFitProber']

class GFitProber(base_prober.BaseProber):
    def setup(self):
        # Queries and suffixes
        self.TIME_WINDOWS = self.parameters.get('time_windows', [24*7])
        self.SUFFIXES = self.parameters.get('suffixes', ['7d'])

        # Assert that both are the same length
        if not len(self.TIME_WINDOWS) == len(self.SUFFIXES):
            raise KeyError('Queries %s and Suffixes %s are not the same length' %
                           (self.TIME_WINDOWS, self.SUFFIXES))

    def collect_data(self):
        service = google_creds.connect_to_api('fitness', 'v1')
        data = {}
        now = time.time()
        utcnow = datetime.datetime.utcnow()

        for hours, suffix in zip(self.TIME_WINDOWS, self.SUFFIXES):
            ndays = utcnow - datetime.timedelta(hours=hours)
            start_time = ndays.isoformat("T") + "Z"
            response = service.users().sessions().list(userId='me', startTime=start_time).execute()

            num_workout = len(response['session'])
            long_workout_count = 0
            time_workout = 0
            for session in response['session']:
                time_workout += ((int(session['endTimeMillis'])-int(session['startTimeMillis'])) / 1000)
                if time_workout >= 30:
                    long_workout_count += 1

            data[self.prefix + '.num_workout.' + suffix] = [(now, num_workout)]
            data[self.prefix + '.num_long_workout.' + suffix] = [(now, long_workout_count)]
            data[self.prefix + '.time_workout.' + suffix] = [(now, time_workout)]
        return data
