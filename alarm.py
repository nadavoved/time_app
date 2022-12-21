import time
from warnings import filterwarnings

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from util import *

filterwarnings('ignore',
               message=r'The localize method is no longer necessary.*')


class Alarm:
    """Alarm class."""

    def __init__(self, dt_obj: datetime, prompt: str = 'TIME OUT!!!'):
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
        self.id = str(self.dt)

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
                                func=cprint, trigger='date',
                                run_date=alarm.dt, args=[alarm.prompt])
        print(highlight(f'Alarm was set on {alarm.id}'))

    def pop(self, index: int):
        """Deactivate alarm if scheduled."""
        job = self.jobs[index - 1]
        self._scheduler.remove_job(job_id=job.id)
        print(highlight(f'\nAlarm on {job.id} was removed.'))

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
            return highlight(res)
        return highlight('\nNo Pending Alarms.\n')


def edit_alarm(scheduler: AlarmScheduler):
    """Add/Remove an alarm to/from a given scheduler.
    Alarm is constructed by user input.
    """

    def remove_alarm():
        print(title('REMOVAL MODE'))
        print(scheduler)
        allowed_values = [str(n) for n in range(1, len(scheduler.jobs) + 1)]
        i = validate_func_input(func=validate_input, prompt='Select an alarm to remove', allowed_values=allowed_values)
        scheduler.pop(int(i))

    def set_alarm():
        print(title('SETTING MODE'))
        print(scheduler)
        dt = validate_func_input(func=validate_date, inp_func=input_date)
        alarm_prompt = input(f'Enter alarm prompt, '
                             f'or press "Enter" to use default one'
                             f' {Fore.GREEN}>>>{Style.RESET_ALL} ')
        clear()
        scheduler.add(Alarm(dt, alarm_prompt))

    while True:
        try:
            if scheduler.has_jobs:
                action = validate_func_input(func=validate_input,
                                             prompt='set or remove an alarm[s/r]?',
                                             allowed_values=['s', 'r', 'S', 'R'])
                if action.lower() == 'r':
                    remove_alarm()
                else:
                    set_alarm()
            else:
                set_alarm()
            break
        except KeyboardInterrupt:
            clear()
            continue


def edit_scheduler(sc: AlarmScheduler, repeated_input=False):
    """edit a scheduler."""
    print(title('ALARM INPUT MODE'))
    if repeated_input:
        while True:
            edit_alarm(sc)
            try:
                input(highlight('\nPress any button to repeat, '
                                '"Ctrl + C" to exit input mode: ', status=True))
                clear()
            except KeyboardInterrupt:
                print(highlight(f'Exiting input mode...'
                                f'Don\'t forget to run the scheduler !', status=True))
                break
    else:
        edit_alarm(sc)
    print(sc)


def run_scheduler(sc: AlarmScheduler):
    print(highlight('Scheduler is up and running...', status=True))
    print(sc)
    sc.exhaust()
