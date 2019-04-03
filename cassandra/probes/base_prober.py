import gzip
import os
import pickle as pkl

import time
import random
import logging


class BaseProber(object):

  def __init__(self, config):
    # We need there to be a prefix and a name otherwise we crash
    self.prefix = config['prefix']
    self.class_name = config['class']
    
    # frequncy and parameters have a default
    self.frequency = config.get('frequency', 5*60)
    self.parameters = config.get('parameters', {})
      
    # Fuzzyfy the starting time to prevent lockstep
    self.next_run = time.time() + random.randint(0, self.frequency)

    self.setup()

    logging.info('Created probe for {}'.format(self.class_name))

  def setup(self):
    pass

  def collect_data(self):
    raise NotImplementedError("Subclasses should implement this!")

  def execute(self):
    """Function to call to get data."""
    data = self.collect_data()

    logging.debug('Probe {} with prefix {} created data {} at {}'.format(self.class_name, self.prefix, str(data), str(int(time.time()))))
    return data
