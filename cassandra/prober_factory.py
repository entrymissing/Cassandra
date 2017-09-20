import os
import glob
import inspect
from cassandra.probes import base_prober

   
class ProberFactory(object):
  
  def __init__(self):
    self._all_probe_classes = {}
    
    files = glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'probes', '*.py'))
    for file in files:
      name = os.path.splitext(os.path.basename(file))[0]
      name = 'cassandra.probes.' + name
      module = __import__(name, fromlist = ['__PROBE_NAME'])
      if '__PROBE_NAME' in dir(module):
        probe_name = getattr(module, '__PROBE_NAME')
        probe_class = getattr(module, probe_name)
        self._all_probe_classes[probe_name] = probe_class

  def get_probe(self, config):
    probe_class = config['class']
    return self._all_probe_classes[probe_class](config)