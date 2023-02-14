import functools

import time

from zoneinfo import ZoneInfo


from datetime import datetime

from dateutil.parser import parse
from display_util import highlight, clear, format_dt

def get_validated_input(validation_func, inp_func=input, prompt: str=None,
                        break_value: str=None, **kwargs):
    """Return a validated output of validation_func, or 'None' if input loop is broken.

    @:param validation_func: (function) a validation function to return a valid output.

    @:param inp_func: (function) an input function to receive input with.
    Default is built-in `input`, custom functions should accept
    at least one argument as an input.
    In addition, they should raise an exception upon an invalid input.

    @:param prompt: (str) a prompt to display for input_func.
    @:param break_value: (str) a value to break input loop upon encounter."""
    if prompt is not None:
        pr_suffix = highlight(' >>> ', color='g')
        prompt += pr_suffix

        def simple_inp_func():
            return inp_func(prompt)

    else:
        def simple_inp_func():
            return inp_func()

    while True:
        try:
            inp = simple_inp_func()
            clear()
            if inp == break_value:
                return None
            else:
                return validation_func(inp, **kwargs)
        except Exception as err:
            print(highlight(str(err).strip('\' '), color='r'))


def validate_known_input(inp, allowed_values):
    """Validate that given input is within allowed values."""
    if inp in allowed_values:
        return inp
    raise ValueError(f'{inp} not in allowed values:{allowed_values}.')


def input_date():
    zone = get_validated_input(validation_func=ZoneInfo,
                               prompt='Enter a timezone, or press '
                                      '"Enter" for the '
                                      'current timezone', break_value='')
    dt = get_validated_input(validation_func=parse, prompt='Enter a date')
    if zone:
        dt = dt.replace(tzinfo=zone)
    return dt


def validate_date(dt):
    """Validate datetime with timezone."""
    print(highlight(f'date: {format_dt(dt)}'))
    now = datetime.now(tz=dt.tzinfo)
    if dt > now:
        return dt
    else:
        raise ValueError('Can\'t set alarm in the past !')


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
                    clear()
                except KeyboardInterrupt:
                    exit()
                else:
                    continue
    return wrapper
