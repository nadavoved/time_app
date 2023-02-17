import time
from warnings import filterwarnings

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from util import display_util, flow_util

filterwarnings('ignore',
               message=r'The localize method is no longer necessary.*')


class Alarm:
    """Alarm class."""

    def __init__(self, dt_obj, prompt: str = 'TIME OUT!!!'):
        """Constructor method.
        :param: dt_obj: a datetime object.
        :type: date: datetime.datetime
        :param: zone: a timezone object.
        :type: zone: ZoneInfo|None
        :param: prompt: A message to display on time.
        :type: prompt: str
        """
        self.dt = dt_obj
        self.prompt = prompt
        self.id = display_util.format_dt(self.dt)

    def __str__(self):
        return f'date: {self.dt}\nprompt: {self.prompt}'


class AlarmScheduler:
    """Scheduler Class."""
    _CACHE_PATH = 'cache/alarm_cache.sqlite'

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
                                func=display_util.cprint, trigger='date',
                                run_date=alarm.dt, args=[alarm.prompt])
        print(display_util.highlight(f'Alarm was set on {alarm.id}'))

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
    print(sc)
    print(display_util.title('REMOVAL MODE'))
    allowed_values = [str(n) for n in range(1, len(sc.jobs) + 1)]
    i = flow_util.get_validated_input(
                            validation_func=flow_util.validate_known_input,
                            prompt='Select an alarm to remove',
                            allowed_values=allowed_values)
    sc.pop(int(i))


def set_alarm(sc: AlarmScheduler):
    print(sc)
    print(display_util.title('SETTING MODE'))
    dt = flow_util.get_validated_input(validation_func=flow_util.validate_date,
                                       inp_func=flow_util.input_date)
    alarm_prompt = input(f'Enter alarm prompt, '
                         f'or press "Enter" to use default one'
                         f'{display_util.highlight(" >>> ", color="g")}')
    display_util.clear()
    sc.add(Alarm(dt, alarm_prompt))


@flow_util.act_on_interrupt
def edit_alarm(sc: AlarmScheduler):
    """Add/Remove an alarm to/from a given scheduler.
    Alarm is constructed by user input.
    """
    if sc.has_jobs:
        action = flow_util.get_validated_input(
                                     validation_func=flow_util.validate_known_input,
                                     prompt=f'{sc}\nSet or remove an alarm[s/r]?',
                                     allowed_values=['s', 'r', 'S', 'R'])
        if action.lower() == 'r':
            remove_alarm(sc)
        else:
            set_alarm(sc)
    else:
        set_alarm(sc)



def edit_scheduler(sc, repeat=False):
    if repeat:
        while True:
            edit_alarm(sc)
    else:
        edit_alarm(sc)


def run_scheduler(sc: AlarmScheduler):
    print(display_util.highlight('Scheduler is up and running...', color='b'))
    print(sc)
    sc.exhaust()
