#!/usr/bin/python

VERSION="pytaVSL v0.0.0"

import argparse
from sys import argv

parser = argparse.ArgumentParser(prog="python %s" % argv[0], formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('--name', help='osc namespace', default='pyta')
parser.add_argument('--port', help='udp port or unix socket path', default=5555)
parser.add_argument('--load', help='image files to load', nargs='+', metavar='FILES')
parser.add_argument('--fps',  help='maximum framerate', type=int, default=25)
parser.add_argument('--max-gpu',  help='maximum gpu memory (in MB)', type=int, default=64)
parser.add_argument('--fullscreen',  help='launch in fullscreen', default=False, action='store_true')
parser.add_argument('--api',  help='print osc api and exit', default=False, action='store_true')
parser.add_argument('--debug',  help='print debug logs', default=False, action='store_true')
parser.add_argument('--geometry',  help='output resolution', type=str, default='800x600', metavar='WIDTHxHEIGHT')
parser.add_argument('--version', action='version', version=VERSION)

args = parser.parse_args()

from pi3d import Log
Log(name=None, level='DEBUG' if args.debug else 'WARNING')

from engine import PytaVSL
geometry = [int(x) for x in args.geometry.split('x')]
pyta = PytaVSL(name=args.name, port=args.port, files=args.load, fps=args.fps, fullscreen=args.fullscreen, width=geometry[0], height=geometry[1])

if args.api:
    pyta.print_api()
else:
    pyta.start()
