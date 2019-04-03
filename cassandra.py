import argparse
import json
import math
import time
import sys
import logging

from cassandra import prober_factory
from cassandra import scheduler
from cassandra import data_writer

from private_data import private_keys


def main(argv):
  logging.basicConfig(filename='example.log',level=logging.CRITICAL)
  # Parse the arguments
  parser = argparse.ArgumentParser()
  parser.add_argument('-c', '--configs', type=str,
                      help="Probe configuration file to use")
  parser.add_argument('--dry_run', action='store_true',
                      help="If set the collection will print the data that "
                           "would have been sent to STDOUT and do nothing "
                           "else.")
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
    # TODO: Make the server and port a command line argument
    writer = data_writer.CarbonPickleWriter(private_keys.CARBON_SERVER,
                                            private_keys.CARBON_PICKLE_PORT)
  
  for probe in all_probers:
    data = probe.execute()
    writer.write_data(data)    
    
  
if __name__ == '__main__':
  main(sys.argv)
