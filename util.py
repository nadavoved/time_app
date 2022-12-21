import functools
import os

from zoneinfo import ZoneInfo

from colorama import Fore, Back, Style
from datetime import datetime

from dateutil.parser import parse


def cprint(inp: str):
    """Print customized foreground and background colors."""
    print(f'{Fore.LIGHTGREEN_EX}{Back.LIGHTBLUE_EX}{inp}{Style.RESET_ALL}')


def validate_func_input(func, inp_func=input, prompt=None,
                        break_value=None, **kwargs):
    """Return a validated return value of func(inp)."""
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
            if break_value is not None and inp == break_value:
                break
            else:
                return func(inp, **kwargs)
        except Exception as err:
            print(highlight(str(err).strip('\' '), color='r'))


def validate_input(inp, allowed_values):
    """Validate string input."""
    if inp in allowed_values:
        return inp
    raise ValueError(f'{inp} not in allowed values:{allowed_values}.')


def input_date():
    zone = validate_func_input(func=ZoneInfo,
                               prompt='Enter a timezone, or press '
                                      '"Enter" for the '
                                      'current timezone', break_value='')
    dt = validate_func_input(func=parse, prompt='Enter a date')
    return dt, zone


def validate_date(dt_and_zone):
    """Validate datetime with timezone."""
    dt, zone = dt_and_zone
    if zone:
        given_time = dt.replace(tzinfo=zone)
    else:
        given_time = dt
    print(highlight(f'date: {given_time}'))
    now = datetime.now(tz=given_time.tzinfo)
    if given_time > now:
        return given_time
    else:
        raise ValueError('Can\'t set alarm in the past !')


def highlight(text, color: str = 'y'):
    suffix = f'{text}{Style.RESET_ALL}'
    match color.lower():
        case 'r' | 'red':
            return f'{Fore.LIGHTYELLOW_EX}{suffix}'
        case 'g' | 'green':
            return f'{Fore.GREEN}{suffix}'
        case 'b' | 'blue':
            return f'{Fore.LIGHTBLUE_EX}{suffix}'
        case 'y' | 'yellow':
            return f'{Fore.LIGHTYELLOW_EX}{suffix}'
        case _:
            return text


def title(text):
    return highlight(f'\n{text}\n{"_" * len(text)}', color='b')


def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def act_on_interrupt(*, shutdown: bool):
    """Decorate a function to allow keyboard interrupt to cause a restart / exit of it."""

    def inner(func):
        @functools.wraps
        def wrapper(*args, **kwargs):
            while True:
                try:
                    func(*args, **kwargs)
                    break
                except KeyboardInterrupt:
                    if not shutdown:
                        continue
                    else:
                        break
        return wrapper
    return inner
