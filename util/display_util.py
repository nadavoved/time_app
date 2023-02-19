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
        return dt.strftime("%m/%d/%Y, %H:%M:%S, %Z, UTC%z")
    else:
        return dt.strftime("%m/%d/%Y, %H:%M:%S")


def format_delta(td: timedelta):
    """Format timedelta as a string, and mention whether it's negative or not."""
    ttl_secs = td.total_seconds()
    is_neg = ttl_secs < 0
    d = {}
    d['days'], rem = divmod(abs(int(ttl_secs)), 60 ** 2 * 24)
    d['hours'], rem = divmod(rem, 60 ** 2)
    d['minutes'], d['seconds']  = divmod(rem, 60)
    lst = []
    for key, value in d.items():
        match value:
            case 1:
                lst.append(f'{value} {key[:-1]}')
            case 0:
                pass
            case _:
                lst.append(f'{value} {key}')
    if len(lst) > 1:
        res = f"{', '.join(lst[:-1])} and {lst[-1]}"
    elif lst:
        res = lst[0]
    else:
        res = '0 seconds'
    return res, is_neg

def format_date_and_delta(dt, delta):
    delta_str, is_neg = format_delta(delta)
    chron_order = {True: 'Before', False: 'In'}
    chron_color = {True: 'r', False: 'y'}
    return highlight(f'date: {format_dt(dt)}\n{chron_order[is_neg]} {delta_str}.',
                    color=chron_color[is_neg])

