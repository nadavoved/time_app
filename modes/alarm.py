import time
from datetime import datetime
from warnings import filterwarnings

import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore


from util import display_util, flow_util, valid_util
from actions import play


filterwarnings('ignore',
               message=r'The localize method is no longer necessary.*')


class Alarm:
    """Alarm class."""

    def __init__(self, dt_obj, repeat: int):
        """Constructor method.
        :param: dt_obj: a datetime object.
        :type: date: datetime.datetime
        :param: zone: a timezone object.
        :type: zone: ZoneInfo|None
        :param: prompt: A message to display on time.
        :type: prompt: str
        """
        self.dt = dt_obj
        self.id = display_util.format_dt(self.dt)
        self.repeat = repeat
    def __str__(self):
        delta = self.dt - datetime.now().astimezone()
        fmt = display_util.format_date_and_delta(self.dt, delta,
                                                 color=False)
        if self.repeat == 1:
            ext = 'Action won\'t repeat.'
        else:
            ext = f'Action will repeat {self.repeat} times.'
        return f'{fmt} {ext}'


class AlarmScheduler:
    """Scheduler Class."""
    _CACHE_PATH = './cache/alarm_cache.sqlite'

    def __init__(self):
        db_url = f'sqlite:///{self._CACHE_PATH}'
        self._scheduler = BackgroundScheduler(
            jobstores={'default': SQLAlchemyJobStore(url=db_url)})
        self._scheduler.start(paused=True)

    def exhaust(self):
        """Run main thread until scheduler is exhausted."""
        self._scheduler.resume()
        while self.has_jobs:
            time.sleep(1)

    def add(self, alarm: Alarm):
        """Schedule a new alarm / rewrite an existing one."""
        self._scheduler.add_job(replace_existing=True, id=alarm.id,
                                func=play, trigger='date',
                                run_date=alarm.dt,
                                args=['sounds/west_guitar.wav', alarm.repeat])
        print(display_util.highlight(f'Alarm was set on {alarm}'))

    def pop(self, index: int):
        """Deactivate alarm if scheduled."""
        job = self.jobs[index - 1]
        self._scheduler.remove_job(job_id=job.id)
        print(display_util.highlight(f'\nAlarm on {job.id} was removed.'))

    def flush(self):
        """Clear Cache."""
        self._scheduler.remove_all_jobs()

    @property
    def has_jobs(self):
        return bool(self.jobs)

    @property
    def jobs(self):
        return self._scheduler.get_jobs()

    def __str__(self):
        if self.has_jobs:
            res = '\nPending Alarms:\n_______________\n'
            for item in enumerate(self.jobs, start=1):
                res += f'({item[0]}) {item[1].id}\n'
            return display_util.highlight(res)
        return display_util.highlight('\nNo Pending Alarms.\n')


def remove_alarm(sc):
    print(display_util.title('REMOVAL MODE'))
    allowed_values = [n for n in range(1, len(sc.jobs) + 1)]
    i = flow_util.get_validated_output(
                            validation_func=valid_util.validate_known_input,
                            prompt=f'{sc}Select an alarm to remove',
                            allowed_values=allowed_values)
    sc.pop(int(i))


def set_alarm(sc: AlarmScheduler, tz_frame):
    print(sc)
    print(display_util.title('SETTING MODE'))
    dt = flow_util.get_validated_output(validation_func=valid_util.validate_date,
                                        tz_frame=tz_frame)
    repeat = flow_util.get_validated_output(validation_func=valid_util.validate_repeat,
                                            prompt='Enter the number of repeats for alarm action')
    sc.add(Alarm(dt, repeat))


@flow_util.act_on_interrupt
def edit_alarm(sc: AlarmScheduler, tz_frame):
    """Add/Remove an alarm to/from a given scheduler.
    Alarm is constructed by user input.
    """
    def edit():
        set_alarm(sc, tz_frame=tz_frame)

    if sc.has_jobs:
        action = flow_util.get_validated_output(
                                     validation_func=valid_util.validate_known_input,
                                     prompt=f'{sc}\nSet or remove an alarm[s/r]?',
                                     allowed_values=['s', 'r', 'S', 'R'])
        if action.lower() == 'r':
            remove_alarm(sc)
        else:
            edit()
    else:
        edit()



def edit_scheduler(sc, repeat=False):
    df = pd.read_parquet(path='./geo_data/tz_sorted.parquet')
    def edit():
        edit_alarm(sc, tz_frame=df)

    if repeat:
        while True:
            edit()
    else:
        edit()

@flow_util.act_on_interrupt
def run_scheduler(sc: AlarmScheduler):
    print(display_util.highlight('Scheduler is up and running...', color='b'))
    print(sc)
    sc.exhaust()
