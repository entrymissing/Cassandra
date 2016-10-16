import gzip
import os
import pickle as pkl
import time

from monitors import gfit_monitor
from monitors import gmail_monitor
from monitors import netstat_monitor
from monitors import ping_monitor
from monitors import test_monitor

AVAILABLE_MONITORS = {'GFitMonitor': gfit_monitor.GFitMonitor,
                      'GmailLengthOfQueryMonitor': gmail_monitor.GmailLengthOfQueryMonitor,
                      'GmailOldestInInboxMonitor': gmail_monitor.GmailOldestInInboxMonitor,
                      'RandomMonitor': test_monitor.RandomMonitor,
                      'PingMonitor': ping_monitor.PingMonitor,
                      'WindowsNetstatMonitor': netstat_monitor.WindowsNetstatMonitor,
                      'LinuxNetstatCollector': netstat_monitor.LinuxNetstatCollector}

def get_monitor(monitor, config):
  if not monitor.get('name') in AVAILABLE_MONITORS:
    raise KeyError('Monitor with name %s not found. Available options are %s' %
                    (monitor.get('name'), ', '.join(AVAILABLE_MONITORS)))
  
  return AVAILABLE_MONITORS.get(monitor.get('name'))(monitor, config)
