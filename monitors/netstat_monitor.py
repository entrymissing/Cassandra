import datetime
import platform
import re
import subprocess
import time

from monitors import base_monitor


class NetstatMonitor(base_monitor.BaseMonitor):

  def setup(self):
    # Time after which we crop data from the local db
    self.MAX_DB_AGE = self.config.get('max_db_age', 14 * 24 * 3600)

    # Time after which we consider it to be a discontinuity and a gap in data (i.e. the machine was off)
    self.GAP_TIME = self.config.get('gap_time', 10 * 60)
    
    # Threshold at which we consider it as distraction (100 kByte)
    self.STREAM_THRESHOLD = self.config.get('stream_threshold', 100 * 1024)

  def init_storage_type(self):
    return {'last_raw_data': (0, 0, 0),
            'data': []}

  def collect_data(self):
    data_points = []

    # Get current and latest data from storage
    now = time.time()
    recv, sent = self.pull_data()
    latest_ts, latest_sent, latest_recv = self.stored_data['last_raw_data']

    # Store new raw data and prune historical data
    self.stored_data['last_raw_data'] = (now, sent, recv)
    while len(self.stored_data['data']) and (now - self.stored_data['data'][0][2]) > self.MAX_DB_AGE:
      self.stored_data['data'].pop(0)

    # Detect a discontinuity and set the values around that event to 0
    if (now - latest_ts) > self.GAP_TIME:
      data_points.append((self.ts_prefix + 'in', 0, latest_ts + self.GAP_TIME/2))
      data_points.append((self.ts_prefix + 'out', 0, latest_ts + self.GAP_TIME/2))
      data_points.append((self.ts_prefix + 'in', 0, now))
      data_points.append((self.ts_prefix + 'out', 0, now))
      
      # Store, dump and return
      self.stored_data['data'].extend(data_points)
      self.dump_data()
      return data_points

    # Calculate the bandwidth usage since the last timestamp in Bytes oer second
    time_diff = now - latest_ts
    sent_bps = (sent - latest_sent) / time_diff
    recv_bps = (recv - latest_recv) / time_diff
    
    # Check for a recv_ or send_ overflow
    if sent_bps < 0 or recv_bps < 0:
      return data_points
    
    # Store and dump
    data_points.append((self.ts_prefix + '.in', recv_bps, now))
    data_points.append((self.ts_prefix + '.out', sent_bps, now))
    self.stored_data['data'].extend(data_points)
    self.dump_data()
    
    # Compute the amount of time above threshold today and last 7d
    time_above_threshold_7d = 0
    time_above_threshold_today = 0
    last_ts = self.stored_data['data'][0][2]
    
    # Todays day
    day_today =  datetime.datetime.fromtimestamp(now).day

    for d in self.stored_data['data']:
      if d[0].endswith('in'):
        if d[1] > self.STREAM_THRESHOLD:
          # Did the data point happen in the last week
          if (now - d[2]) < 7 * 24 * 60 *60:
            time_above_threshold_7d += (d[2] - last_ts)
          
            # Did the datapoint happen today
            if day_today == datetime.datetime.fromtimestamp(d[2]).day:
              time_above_threshold_today += (d[2] - last_ts)
      
      last_ts = d[2]
    data_points.append((self.ts_prefix + '.consuming_7d', time_above_threshold_7d, now))
    data_points.append((self.ts_prefix + '.consuming_today', time_above_threshold_today, now))
    return data_points


class WindowsNetstatMonitor(NetstatMonitor):

  def pull_data(self):
    netstat_proc = subprocess.Popen(['netstat', '-e'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in iter(netstat_proc.stdout.readline, b''):
      # I hate the bloody byte objects
      line = line.decode('utf-8').strip()
      if 'Bytes' in line:
        return float(line.split()[1]), float(line.split()[2])
 
 
class LinuxNetstatCollector(NetstatMonitor):

  def pull_data(self):
    netstat = subprocess.Popen(['netstat', '-ibI', 'en0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stat_line = netstat.stdout.readlines()[1]
    recv_bytes = float(stat_line.split()[6])
    sent_bytes = float(stat_line.split()[7])
    return sent_bytes, recv_bytes