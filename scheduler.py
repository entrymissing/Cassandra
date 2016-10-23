from __future__ import print_function

import argparse
import json
import sys
from tendo import singleton
import time

from monitors import factory
import submitter

def main(argv):
  # Parse the arguments
  parser = argparse.ArgumentParser()
  parser.add_argument('-s', '--settings', type=str,
                      help="Settings file to use", required=True)
  parser.add_argument('--dry_run', action='store_true',
                      help="If set the collection will print the data that would have been sent to STDOUT and do nothing else.")
  parser.add_argument('-d', '--daemon', action='store_true',
                      help="Run as a daemon, i.e. keep running.")
  args = parser.parse_args()

  # Exit if there are multiple instances
  me = singleton.SingleInstance()
  
  # This is used to stop the daemon if e.g. a new verison has been loaded
  with open('version') as fp:
    version = fp.read()

  # Read settings
  with open(args.settings) as fp:
    settings = json.loads(fp.read())

  # Create the monitors
  all_monitors = []
  for mon_settings in settings:
    all_monitors.append(factory.get_monitor(mon_settings['monitor'],
                                            mon_settings['config']))

  # Daemon loop
  while True:
    data = []
    for mon in all_monitors:
      print(mon.name())
      data.extend(mon.monitor())
    if data:
      if args.dry_run:
        for d in data:
          submitter.printer_submitter(d)
      else:
        submitter.carbon_pickle_submitter(data)
    
    if not args.daemon:
      break

    with open('version') as fp:
      if not version == fp.read():
        break

    time.sleep(30)


if __name__ == '__main__':
  main(sys.argv)
