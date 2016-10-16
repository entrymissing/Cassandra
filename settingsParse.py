from __future__ import print_function

import json
import os

_REQUIRED_SECTIONS = ['General', 'Config']

def read_settings(filename):
  # Read settings
  if not os.path.exists(filename):
    raise IOError('File %s not found' % filename)

  with open(filename) as fp:
    config = json.loads(fp.read())

  return config
