import random
import time
import urllib.request

from cassandra.probes import base_prober

__PROBE_NAME = 'ExternalIpProber'

class ExternalIpProber(base_prober.BaseProber):
  def IP2Int(self, ip):
    o = ip.split('.')
    res = (16777216 * int(o[0])) + (65536 * int(o[1])) + (256 * int(o[2])) + int(o[3])
    return res

  def collect_data(self):
    ext_ip = urllib.request.urlopen('https://api.ipify.org').read().decode('ASCII')
    return {self.prefix + '.external_ip': [(time.time(), self.IP2Int(ext_ip))]}
