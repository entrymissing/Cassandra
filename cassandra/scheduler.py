from cassandra import data_writer

class Scheduler(object):

  def __init__(self, probers, writer=data_writer.BaseWriter(),
               version_file='version'):
    self.probers = probers
    self.writer = writer
    self.version_file = version_file
    
    # Read the version from the version file. This is used to stop the daemon if
    # a new verison has been pushed
    with open(self.version_file) as fp:
      self.version = fp.read()
    
  def run(self):
    while True:
      # Find the next scheduled probers
      lowest_scheduled_time = float('inf')
      idx = len(self.probers) + 1
      for i,p in enumerate(self.probers):
        if lowest_scheduled_time > p.next_run:
          idx = i
          lowest_scheduled_time = p.next_run
      data = self.probers[idx].execute()
      self.writer.write_data(data)
      
      # Exit if the version has changed
      with open(self.version_file) as fp:
        if self.version != fp.read():
          break
