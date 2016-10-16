import gzip
import os
import pickle as pkl
import time


class BaseMonitor(object):

  def __init__(self, monitor, config):
    self.frequency = monitor.get('frequency', 5*60)
    self.ts_prefix = monitor['ts_prefix']
    self.config = config

    # Load data for this class. If it doesn't exist init it.
    if not os.path.exists(self.get_storage_filename()):
      self.stored_data = self.init_storage_type()
      self.last_successful_run = 0
    else:
      with gzip.open(self.get_storage_filename(), 'rb') as fp:
        self.last_successful_run, self.stored_data = pkl.load(fp)

    self.setup()

  def init_storage_type(self):
    return []
  
  def name(self):
    return self.__class__.__name__
  
  def get_storage_filename(self):
    return 'data/%s.zip' % type(self).__name__
  
  def dump_data(self):
    with gzip.open(self.get_storage_filename(), 'wb') as fp:
      pkl.dump((self.last_successful_run, self.stored_data), fp)

  def setup(self):
    pass

  def collect_data(self):
    raise NotImplementedError("Subclasses should implement this!")

  def monitor(self):
    """Function to call to get data."""
    # Check if it is time to grab new data
    if (time.time() - self.last_successful_run) > self.frequency:
      try:
        data = self.collect_data()
      except KeyError as e:
        # We don't stop for errors
        print(e) 
        data = []

      # On successful data grabs we update the timestamp and write internal data to disc
      if data:
        self.last_successful_run = time.time()
        self.dump_data()
      return data

    return []
