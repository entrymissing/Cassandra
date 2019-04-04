import datetime
from dateutil.parser import parse
import time

from cassandra.probes import base_prober
from cassandra import google_api_lib as google_api
from cassandra import google_api_credentials_lib as google_creds

__PROBE_NAME = ['GCalendarProber']

class GCalendarProber(base_prober.BaseProber):
    def setup(self):
        # Queries and suffixes
        self.TIME_WINDOWS = self.parameters.get('time_windows', [24*7])
        self.SUFFIXES = self.parameters.get('suffixes', ['7d'])

        # Assert that both are the same length
        if not len(self.TIME_WINDOWS) == len(self.SUFFIXES):
            raise KeyError('Queries %s and Suffixes %s are not the same length' %
                           (self.TIME_WINDOWS, self.SUFFIXES))

    def collect_data(self):
        service = google_creds.connect_to_api('calendar', 'v3')
        data = {}
        now = time.time()

        for hours, suffix in zip(self.TIME_WINDOWS, self.SUFFIXES):
            # TODO: Get Search prefix and calendar from configs
            events = google_api.GetCalendarEntriesByQuery(service, "S-", hours, "Tracking")

            seconds_since = []
            long_count = 0
            short_count = 0
            for event in events:
                start_time = parse(event['start'].get('dateTime'))
                end_time = parse(event['end'].get('dateTime'))
                seconds_since.append(
                    (datetime.datetime.now(datetime.timezone.utc) - start_time).total_seconds())
                event_length = end_time - start_time
                if event_length.seconds <= 30*60:
                    short_count += 1
                else:
                    long_count += 1

            data[self.prefix + '.s_count.' + suffix] = [(now, len(events))]
            data[self.prefix + '.s_seconds_since.' + suffix] = [(now, min(seconds_since))]
            data[self.prefix + '.s_short_count.' + suffix] = [(now, short_count)]
            data[self.prefix + '.s_long_count.' + suffix] = [(now, long_count)]

        return data
