import random
import time

from monitors import base_monitor

class RandomMonitor(base_monitor.BaseMonitor):
  def collect_data(self):
    return [(self.ts_prefix + '.randint', random.randint(1,100), time.time())]
