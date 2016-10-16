import time

from monitors import base_monitor
from monitors import google_api_lib as google_api

class GmailLengthOfQueryMonitor(base_monitor.BaseMonitor):
  def setup(self):
    # Queries and suffixes
    self.QUERIES = self.config['queries']
    self.SUFFIXES = self.config['suffixes']
    
    # Assert that both are the same length
    if not len(self.QUERIES) == len(self.SUFFIXES):
      raise KeyError('Queries %s and Suffixes %s are not the same length' %
          (self.QUERIES, self.SUFFIXES))

  def collect_data(self):
    service = google_api.connect_to_api('gmail', 'v1')
    
    data = []
    now = time.time()
    
    for q, s in zip(self.QUERIES, self.SUFFIXES):
      mails = google_api.ListMessagesMatchingQuery(service, q)
      thread_ids = [m['threadId'] for m in mails]
      data.append((self.ts_prefix + '.' + s, len(set(thread_ids)), now))

    return data

    
class GmailOldestInInboxMonitor(base_monitor.BaseMonitor):
  def collect_data(self):
    service = google_api.connect_to_api('gmail', 'v1')
    
    now = time.time()
    
    mails = google_api.ListMessagesMatchingQuery(service, 'in:inbox')
    thread_age = {}

    if len(mails) == 0:
      return [(self.ts_prefix + '.inbox_oldest', 0, now)]

    for m in mails:
      thread_id = m['threadId']
      msg = google_api.GetMessage(service, 'me', m['id'])
      age = now - (int(msg['internalDate'])/1000)
      if thread_id not in thread_age:
        thread_age[thread_id] = age
      else:
        if age < thread_age[thread_id]:
          thread_age[thread_id] = age

    return [(self.ts_prefix + '.inbox_oldest', max(thread_age.values()), now)]