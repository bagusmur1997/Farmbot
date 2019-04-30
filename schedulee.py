import schedule
import threading
import time

# this is a class which uses inheritance to act as a normal Scheduler,
# but also can run_continuously() in another thread
class ContinuousScheduler(schedule.Scheduler):
      def run_continuously(self, interval=1):
            """Continuously run, while executing pending jobs at each elapsed
            time interval.
            @return cease_continuous_run: threading.Event which can be set to
            cease continuous run.
            Please note that it is *intended behavior that run_continuously()
            does not run missed jobs*. For example, if you've registered a job
            that should run every minute and you set a continuous run interval
            of one hour then your job won't be run 60 times at each interval but
            only once.
            """
            cease_continuous_run = threading.Event()

            class ScheduleThread(threading.Thread):
                @classmethod
                def run(cls):
                    # I've extended this a bit by adding self.jobs is None
                    # now it will stop running if there are no jobs stored on this schedule
                    while not cease_continuous_run.is_set() and self.jobs:
                        # for debugging
                        # print("ccr_flag: {0}, no. of jobs: {1}".format(cease_continuous_run.is_set(), len(self.jobs)))
                        self.run_pending()
                        time.sleep(interval)

            continuous_thread = ScheduleThread()
            continuous_thread.start()
            return cease_continuous_run

''' # example using this custom scheduler that can be run in a separate thread
your_schedule = ContinuousScheduler()
your_schedule.every().day.do(print)

# it returns a threading.Event when you start it.
halt_schedule_flag = your_schedule.run_continuously()

# you can now do whatever else you like here while that runs

# if your main script doesn't stop the background thread, it will keep running
# and the main script will have to wait forever for it

# if you want to stop it running, just set the flag using set()
halt_schedule_flag.set()

# I've added another way you can stop the schedule to the class above
# if all the jobs are gone it stops, and you can remove all jobs with clear()
your_schedule.clear()

# the third way to empty the schedule is by using Single Run Jobs only
# single run jobs return schedule.CancelJob

def job_that_executes_once():
    # Do some work ...
    print("I'm only going to run once!")
    return schedule.CancelJob

# using a different schedule for this example to avoid some threading issues
another_schedule = ContinuousScheduler()
another_schedule.every(5).seconds.do(job_that_executes_once)
halt_schedule_flag = another_schedule.run_continuously()
'''
