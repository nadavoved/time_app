import functools
import time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from datetime import datetime, timedelta

import pandas as pd
from dateutil.parser import parse

from util.display_util import highlight, clear, format_dt, format_delta


def get_validated_output(*, validation_func, prompt: str=None,
                         break_value: str=None, **kwargs):
    """Return a validated output of validation_func, or 'None' if loop is broken.

    @:param validation_func: (function) a validation function to return a valid output.
    Function should raise an exception upon an invalid input.
    @:param prompt: (str) a prompt to display for validation_func.
    If None given, no input will be asked.
    @:param break_value: (str) a value to break input loop upon encounter.
    """
    if prompt is not None:
        pr_suffix = highlight(' >>> ', color='g')
        prompt += pr_suffix
        def inner_action():
            inp = input(prompt)
            clear()
            if inp == break_value:
                return None
            else:
                return validation_func(inp, **kwargs)
    else:
        def inner_action():
            return validation_func(**kwargs)

    while True:
        try:
            return inner_action()
        except Exception as err:
            print(highlight(str(err).strip('\' '), color='r'))


def validate_known_input(inp, allowed_values):
    """Validate that given input is within allowed values."""
    allowed_values = list(map(str, allowed_values))
    if inp in allowed_values:
        return inp
    allowed_str = ",".join(list(allowed_values))
    raise ValueError(f'{inp} not in allowed values: {allowed_str}.')

def validate_date(tz_frame):
    """Validate datetime with timezone."""
    zone = get_validated_output(validation_func=validate_tz,
                                prompt='Enter a timezone, or press '
                                      '"Enter" for the '
                                      'current timezone',
                                break_value='',
                                tz_frame=tz_frame)
    dt = get_validated_output(validation_func=parse, prompt='Enter a date',
                              ignoretz=True)
    if zone:
        dt = dt.replace(tzinfo=zone)
    else:
        dt = dt.astimezone()
    delta = dt - datetime.now().astimezone()
    print(highlight(f'date: {format_dt(dt)} ({format_delta(delta)} from now)'))
    if delta > timedelta():
        return dt
    else:
        raise ValueError('Can\'t set alarm in the past !')


def validate_tz(tz_str: str, tz_frame):
    """Return a valid IANA timezone from a given string.
    Given String can be either a specific city / province, or a country.
    """
    q_iter = (item for item in tz_frame if item not in
              ('continent', 'population'))
    for item in q_iter:
        res = tz_frame[tz_frame[item] == tz_str] \
            .drop_duplicates(subset=['utc_offset'])
        if not res.empty:
            n = len(res)
            if n > 1:
                res.index = range(1, n + 1)
                menu = res[['tz_name', 'utc_offset']]
                prompt = (highlight(f"{tz_str} has {n} time zones:\n"
                          f"Select a number from the given menu\n{menu}\n"))
                sel = get_validated_output(validation_func=validate_known_input,
                                           prompt=prompt, allowed_values=list(res.index))
                tz = res.loc[int(sel), 'timezone']
            else:
                tz = res.iloc[0].timezone
            return ZoneInfo(tz)
    raise ZoneInfoNotFoundError(f'No such zone as "{tz_str}"!')

def act_on_interrupt(func):
    """Decorate a function to go back on a keyboard interrupt.
     Single tap causes a restart, double tap causes an exit.
     """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except KeyboardInterrupt:
                clear()
                try:
                    print(highlight('Press Ctrl + C again to quit...', 'r'))
                    time.sleep(0.5)
                except KeyboardInterrupt:
                    exit()
                else:
                    continue
                finally:
                    clear()

    return wrapper
