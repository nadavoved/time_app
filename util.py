import os

from zoneinfo import ZoneInfo

from colorama import Fore, Back, Style
from datetime import datetime

from dateutil.parser import parse


def cprint(inp: str):
    """Print customized foreground and background colors."""
    print(f'{Fore.LIGHTYELLOW_EX}{Back.LIGHTBLUE_EX}{inp}{Style.RESET_ALL}')


def validate_func_input(func, inp_func=input, prompt=None,
                        break_value=None, **kwargs):
    """Return a validated return value of func(inp)."""
    if prompt is not None:
        pr_suffix = f' {Fore.GREEN}>>>{Style.RESET_ALL} '
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
            print(f'{Fore.RED}{err}{Style.RESET_ALL}'.strip('\' '))


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


def highlight(text, status=False):
    if not status:
        return f'{Fore.LIGHTYELLOW_EX}{text}{Style.RESET_ALL}'
    return f'{Fore.LIGHTBLUE_EX}{text}{Style.RESET_ALL}'


def title(text):
    return highlight(f'\n{text}\n{"_" * len(text)}', status=True)


def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
