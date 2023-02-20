from zoneinfo import ZoneInfoNotFoundError
from datetime import datetime, timedelta, timezone

from dateutil.parser import parse

from util.flow_util import get_validated_output
from util.display_util import highlight, format_date_and_delta

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
    print(format_date_and_delta(dt, delta))
    if delta > timedelta():
        return dt
    else:
        raise ValueError('Can\'t set alarm in the past !')


def validate_tz(tz_str: str, tz_frame):
    """Return a valid IANA timezone from a given string.
    Given String can be either a specific city / province, or a country.
    """
    q_lst = ['name', 'abbreviation', 'offset_str', 'country']
    for item in q_lst:
        res = tz_frame[tz_frame[item] == tz_str].drop_duplicates(subset=['gmt_offset'])
        if not res.empty:
            n = len(res)
            if n > 1:
                val_lst = list(range(1, n + 1))
                res.index = [f'({i})' for i in val_lst]
                view_list = list(filter(lambda x: x != item, q_lst))
                slc = res[view_list]
                menu = slc.rename(columns=lambda s: s.replace('_', ' ').split()[0].title())
                sub_prompt = highlight(f"{tz_str} refers to {n} time zones.\n"
                                       f"Select a number from the given menu:", color='b')
                menu_txt = highlight(f'\n{menu}\n')
                prompt = sub_prompt + menu_txt
                sel = get_validated_output(validation_func=validate_known_input,
                                           prompt=prompt, allowed_values=val_lst)
                i = int(sel) - 1
            else:
                i = 0
            offset = int(res.gmt_offset_minute.iloc[i])
            return timezone(offset=timedelta(minutes=offset))
    raise ZoneInfoNotFoundError(f'No time zone found referring to "{tz_str}".')