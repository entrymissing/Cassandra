import argparse
import json
import logging
import math
from tendo import singleton
import time
import sys

from cassandra import prober_factory
from cassandra import scheduler
from cassandra import data_writer


def main(argv):
  logging.basicConfig(filename='example.log',level=logging.DEBUG)
  
  # Exit if there are multiple instances
  singleton.SingleInstance()

  # Parse the arguments
  parser = argparse.ArgumentParser()
  parser.add_argument('-c', '--configs', type=str,
                      help="Probe configuration file to use")
  parser.add_argument('--dry_run', action='store_true',
                      help="If set the collection will print the data that "
                           "would have been sent to STDOUT and do nothing "
                           "else.")
  parser.add_argument('-d', '--daemon', action='store_true',
                      help="Run as a daemon, i.e. keep running.")
  args = parser.parse_args()
  
  # Read settings
  with open(args.configs) as fp:
    configs = json.loads(fp.read())
  
  factory = prober_factory.ProberFactory()
  all_probers = []
  for config in configs:
    all_probers.append(factory.get_probe(config))
  
  if args.dry_run:
    writer = data_writer.BaseWriter()
  else:
    writer = data_writer.CarbonPickleWriter('entrymissing.net', 2004)
    
  s = scheduler.Scheduler(all_probers,
                          writer,
                          version_file='version')
  s.run()
    
  
if __name__ == '__main__':
  main(sys.argv)