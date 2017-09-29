import time

from cassandra.probes import base_prober
from cassandra import google_api_lib as google_api

__PROBE_NAME = ['GmailLengthOfQueryProber',
                'GmailOldestInInboxProber']

class GmailLengthOfQueryProber(base_prober.BaseProber):
  def setup(self):
    # Queries and suffixes
    self.QUERIES = self.parameters['queries']
    self.SUFFIXES = self.parameters['suffixes']
    
    # Assert that both are the same length
    if not len(self.QUERIES) == len(self.SUFFIXES):
      raise KeyError('Queries %s and Suffixes %s are not the same length' %
          (self.QUERIES, self.SUFFIXES))

  def collect_data(self):
    service = google_api.connect_to_api('gmail', 'v1')
    
    data = {}
    now = time.time()
    
    for q, s in zip(self.QUERIES, self.SUFFIXES):
      mails = google_api.ListMessagesMatchingQuery(service, q)
      thread_ids = [m['threadId'] for m in mails]
      data[self.prefix + '.' + s] = [(now, len(set(thread_ids)))]

    return data

class GmailOldestInInboxProber(base_prober.BaseProber):
  def collect_data(self):
    service = google_api.connect_to_api('gmail', 'v1')
    
    now = time.time()
    
    mails = google_api.ListMessagesMatchingQuery(service, 'in:inbox')
    thread_age = {}

    if len(mails) == 0:
      return {self.prefix + '.inbox_oldest': [(now, 0)]}

    for m in mails:
      thread_id = m['threadId']
      msg = google_api.GetMessage(service, 'me', m['id'])
      age = now - (int(msg['internalDate'])/1000)
      if thread_id not in thread_age:
        thread_age[thread_id] = age
      else:
        if age < thread_age[thread_id]:
          thread_age[thread_id] = age

    return {self.prefix + '.inbox_oldest': [(now, max(thread_age.values()))]}
 