import sched, time

class CronScheduler(sched.scheduler):

  def add_cron(self, job, every_n_seconds, argument=(), kwargs={}):
    self.enter(every_n_seconds, 0, self.add_cron, argument=(job, every_n_seconds, argument, kwargs))
    self.enter(every_n_seconds, 5, job, argument=argument, kwargs=kwargs)

def test_a(x):
  print("Hello every 3" + x)

def test_b():
  print("Hello every 2")

if __name__ == "__main__":
  s = CronScheduler()
  s.add_cron(test_a, 3, argument=('asfd',))
  s.add_cron(test_b, 2)
  s.run()
