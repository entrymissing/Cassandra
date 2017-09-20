import random
import time

from cassandra.probes import base_prober

__PROBE_NAME = 'RandomProber'

class RandomProber(base_prober.BaseProber):
  
  def collect_data(self):
    return {self.prefix + '.randint': [(time.time(), random.randint(1,100)),
                                       (time.time()-1, random.randint(101,200))]}
