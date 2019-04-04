""" cassandra.py is the main entry module for the prober service
"""

import argparse
import json
import sys
import logging

from cassandra import prober_factory
from cassandra import data_writer

def main(_):
    """The main function."""
    logging.basicConfig(filename='cassandra.log', level=logging.ERROR)

    # Parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--configs', type=str,
                        help="Probe configuration file to use")
    parser.add_argument('--dry_run', action='store_true',
                        help="If set the collection will print the data that "
                             "would have been sent to STDOUT and do nothing "
                             "else.")
    parser.add_argument('-s', '--carbon_server', type=str, default='localhost',
                        help="DNS of the server that carbon is running on. Default is localhost.")
    parser.add_argument('-p', '--carbon_port', type=int, default=2004,
                        help="Pickle port of the carbon server. Default is 2004.")
    args = parser.parse_args()

    # Read settings
    with open(args.configs) as file_handle:
        configs = json.loads(file_handle.read())

    factory = prober_factory.ProberFactory()
    all_probers = []
    for config in configs:
        all_probers.append(factory.get_probe(config))

    if args.dry_run:
        writer = data_writer.BaseWriter()
    else:
        writer = data_writer.CarbonPickleWriter(args.carbon_server, args.carbon_port)

    data = {}
    for probe in all_probers:
        data.update(probe.execute())
    writer.write_data(data)

if __name__ == '__main__':
    main(sys.argv)
