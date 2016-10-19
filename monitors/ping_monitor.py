import platform
import re
import subprocess
import time

from monitors import base_monitor


class PingMonitor(base_monitor.BaseMonitor):
  def setup(self):
    self.MAX_LINES = 1000
    self.num_pings = self.config.get('num_pings', 5)
    self.ping_targets = self.config.get('ping_targets', [])

    WINDOWS_RE = 'Minimum = (\d+)ms, Maximum = (\d+)ms, Average = (\d+)ms'
    LINUX_RE = 'rtt min/avg/max/mdev = (.*)/(.*)/(.*)/(.*) ms'
    if platform.system().lower() == 'windows':
      self.MATCHING_RE = WINDOWS_RE
      self.PING_COMMAND = 'ping %s -n ' + str(self.num_pings)
      self.IS_WINDOWS =  True
    else:
      self.MATCHING_RE = LINUX_RE
      self.PING_COMMAND = ['ping', '-c', str(self.num_pings)]
      self.IS_WINDOWS =  False
      

  def collect_data(self):
    data_points = []

    for target in self.ping_targets:
      if self.IS_WINDOWS:
        cmd = self.PING_COMMAND % target
      else:
        cmd = self.PING_COMMAND + [target]
      ping_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
      for line in iter(ping_proc.stdout.readline, b''):
        # I hate the bloody byte objects
        line = line.decode('utf-8')
        m = re.match(self.MATCHING_RE, str(line).strip())
        if m:
          if self.IS_WINDOWS:
            avg = float(m.group(3))
          else:
            avg = float(m.group(2))
          data_points.append((self.ts_prefix + '.' + target.replace('.', '_') , avg, time.time()))
          break
    return data_points
