import argparse

import pandas as pd

from util import display_util
from alarm import run_scheduler, edit_scheduler, AlarmScheduler


def gen_alarm_parser(sub_parser):
    parser = sub_parser.add_parser(name='alarm')
    parser.add_argument('-e', '--edit', action='store_true', help='Edit alarms. Default is to run existing.')
    parser.add_argument('-r', '--repeat', action='store_true', help='Add/remove multiple alarms.')
    parser.add_argument('-f', '--flush', action='store_true', help='Clear the scheduler.')


def gen_timer_parser(sub_parser):
    parser = sub_parser.add_parser(name='timer')
    parser.add_argument('interval', help='Time interval.')
    parser.add_argument('-u', '--unit', help='Specify input unit. Default is seconds.')
    parser.add_argument('-r', '--repeat', action='store_true',
                        help='Repeat every given interval.')


def gen_stopwatch_parser(sub_parser):
    sub_parser.add_parser(name='stopwatch')


def gen_converter_parser(sub_parser):
    parser = sub_parser.add_parser(name='converter')
    # add subparsers:
    conv_modes = parser.add_subparsers(title='converter modes', dest='conv_mode')
    tz_parser = conv_modes.add_parser(name='tz')
    unit_parser = conv_modes.add_parser(name='unit')
    # tz args:
    tz_parser.add_argument('time', help='Time to convert.')
    tz_parser.add_argument('--from', help='Timezone to convert from. Default is the current timezone.')
    tz_parser.add_argument('--to', help='Timezone to convert to. Default is GMT.')
    # unit args:
    unit_parser.add_argument('interval', help='Time interval.')
    # TODO - update units according to implementation of converter
    unit_parser.add_argument('--from', help='Specify input unit. Default is seconds.')
    unit_parser.add_argument('--to', help='Specify required unit. Default is seconds.')


def get_args():
    desc = ('A time app.\nHas 4 modes:\n\t'
            '1. Alarm\n\t2. Timer\n\t3. Stopwatch\n\t4. Timezone/unit converter')
    main_parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawTextHelpFormatter)
    modes = main_parser.add_subparsers(title='modes', required=True, dest='mode')
    gen_alarm_parser(modes)
    gen_timer_parser(modes)
    gen_stopwatch_parser(modes)
    gen_converter_parser(modes)
    return main_parser.parse_args()


if __name__ == '__main__':
    display_util.clear()
    args = get_args()
    match args.mode:
        case 'alarm':
            sc = AlarmScheduler()
            if args.flush:
                sc.flush()
                print(display_util.highlight('Cleared alarm cache', color='y'))
            elif args.edit: # TODO - check status of scheduler while editing
                df = pd.read_parquet(path='geo_data/tz_db/tz_dictionary.parquet')
                edit_scheduler(sc, tz_frame=df, repeat=args.repeat)
            else:
                run_scheduler(sc)
        case 'timer':
            pass
        case 'stopwatch':
            pass
        case 'converter':
            pass
