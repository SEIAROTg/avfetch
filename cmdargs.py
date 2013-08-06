# -*- coding: utf-8 -*-

import argparse

help_message = """\
avfetch, a command-line online audio/video downloader.
usage: avfetch [OPTION]... {URL|JOB}

  -e,  --engine=ENGINE      specify a engine manually
  -f,  --format             format output job
  -h,  --help               show this help
  -l,  --lang=LANGUAGE      specify language for a job
       --no-combine         do not combine segments after downloading
  -o,  --output=PATH        specify output file path for a job
  -p,  --pass=PASSWORD      specify password for a job
  -q,  --quality=QUALITY    specify quality for a job
  -r,  --resolve            resolve downloading url but do not download
       --restart            resolve again even if there is resolved file list
  -v,  --verbose            be verbose"""

parser = argparse.ArgumentParser(
    prog='avfetch', 
    description='avfetch, a command-line online audio/video downloader.', 
    add_help=False, 
    usage='avfetch [OPTION]... {URL|JOB}',
    formatter_class=argparse.RawDescriptionHelpFormatter
)

options = parser.add_argument_group()
options.add_argument(
    '-d', '--download',
    action='store_const', const='download', dest='action'
)
options.add_argument(
    '-e', '--engine',
    nargs=1, metavar='engine', action='store', dest='engine'
)
options.add_argument(
    '-f', '--format',
    action='store_true', dest='format'
)
options.add_argument(
    '-h', '--help',
    action='store_const', const='help', dest='action'
)
options.add_argument(
    '-l', '--list',
    action='store_const', const='list', dest='action'
)
options.add_argument(
    '--lang',
    nargs=1, metavar='language', action='append', dest='lang'
)
options.add_argument(
    '--no-combine',
    action='store_false', dest='combine'
)
options.add_argument(
    '-o', '--output',
    nargs=1, metavar='path', action='store', dest='path'
)
options.add_argument(
    '-p', '--password',
    nargs='?', metavar='password', action='append', dest='password'
)
options.add_argument(
    '-q', '--quality',
    nargs=1, metavar='quality', action='append', dest='quality'
)
options.add_argument(
    '-r', '--resolve',
    action='store_const', const='resolve', dest='action'
)
options.add_argument(
    '--restart',
    action='store_true', dest='restart'
)
options.add_argument(
    '-v', '--verbose',
    action='count', dest='verbose'
)
options.add_argument(
    'jobfile',
    action='store', nargs='?'
)
def parse():
    global parser
    args = parser.parse_args()
    if args.engine:
        args.engine = args.engine[0]
    if args.action == None:
        args.action = 'download'
    elif args.action == 'help':
        print help_message
        import sys
        sys.exit(0)
    return args