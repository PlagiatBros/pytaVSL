#!/usr/bin/python

import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('--name', help='osc namespace', default='pyta')
parser.add_argument('--port', help='udp port or unix socket path', default=5555)
parser.add_argument('--load', help='image files to load', nargs='+', metavar='FILES')
parser.add_argument('--fps',  help='maximum framerate', type=int, default=25)
parser.add_argument('--fullscreen',  help='launch in fullscreen', default=False, action='store_true')
parser.add_argument('--api',  help='print osc api and exit', default=False, action='store_true')
parser.add_argument('--log',  help='verbosity level', default='warning', choices=['debug', 'info', 'warning', 'error', 'critical'])

args = parser.parse_args()

from pi3d import Log
Log(name=None, level=args.log.upper())

from engine import PytaVSL
pyta = PytaVSL(name=args.name, port=args.port, files=args.load, fps=args.fps, fullscreen=args.fullscreen)

if args.api:
    pyta.print_api()
else:
    pyta.start()
