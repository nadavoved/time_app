import os

from colorama import Fore, Back, Style
from datetime import datetime, timedelta


def cprint(inp: str):
    """Print customized foreground and background colors."""
    print(f'{Fore.LIGHTGREEN_EX}{Back.LIGHTBLUE_EX}{inp}{Style.RESET_ALL}')


def title(text):
    """Return text as underscored and blue."""
    return highlight(f'\n{text}\n{"_" * len(text)}', color='b')


def highlight(text, color: str = 'y'):
    """Return given text in the given color."""
    suffix = f'{text}{Style.RESET_ALL}'
    match color.lower():
        case 'r' | 'red':
            return f'{Fore.LIGHTRED_EX}{suffix}'
        case 'g' | 'green':
            return f'{Fore.GREEN}{suffix}'
        case 'b' | 'blue':
            return f'{Fore.LIGHTBLUE_EX}{suffix}'
        case 'y' | 'yellow':
            return f'{Fore.LIGHTYELLOW_EX}{suffix}'
        case _:
            return text


def clear():
    """Clear current cli output."""
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def format_dt(dt: datetime):
    """Format datetime to string."""
    if dt.tzinfo:
        return dt.strftime("%m/%d/%Y, %H:%M:%S, %Z")
    else:
        return dt.strftime("%m/%d/%Y, %H:%M:%S")


def format_delta(td: timedelta):
    """Format timedelta to string."""
    days = td.days
    hours, seconds_rem = divmod(td.total_seconds(), 3600)
    minutes, seconds = divmod(seconds_rem, 60)
    z = zip((days, hours, minutes, seconds), ('d', 'h', 'm', 's'))
    d = {label: item for item, label in z if item > 0}

