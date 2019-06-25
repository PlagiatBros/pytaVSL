#!/usr/bin/python3
# encoding: utf-8


VERSION="pytaVSL v0.0.0"

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from sys import argv, path, version_info, exit

if version_info[0] != 3:
    print('Error: Python 3 is required to run pytaVSL')
    exit(0)

path.append('engine')
path.append('slides')
path.append('shaders')

parser = ArgumentParser(prog="python3 %s" % argv[0], formatter_class=ArgumentDefaultsHelpFormatter)

parser.add_argument('--namespace', help='osc namespace', default='pyta')
parser.add_argument('--port', help='udp port or unix socket path', default=5555)
parser.add_argument('--load', help='image files to load', nargs='+', metavar='FILES')
parser.add_argument('--text', help='text objects to create', nargs='+', metavar='NAME:FONT', default=["0:sans", "1:sans", "2:mono", "3:mono"])
parser.add_argument('--fps',  help='maximum framerate, 0 for free wheeling', type=int, default=25)
parser.add_argument('--max-vram',  help='maximum video memory allocation (in MB)', type=int, default=64)
parser.add_argument('--memtest',  help='test video memory size', default=False, action='store_true')
# parser.add_argument('--fullscreen',  help='launch in fullscreen', default=False, action='store_true')
parser.add_argument('--api',  help='print osc api and exit', default=False, action='store_true')
parser.add_argument('--debug',  help='print debug logs', default=False, action='store_true')
parser.add_argument('--show-fps',  help='show fps', default=False, action='store_true')
parser.add_argument('--resolution',  help='output resolution', type=str, default='800x600', metavar='WIDTHxHEIGHT')
parser.add_argument('--title',  help='window title', type=str, default='pytaVSL', metavar='TITLE')
parser.add_argument('--version', action='version', version=VERSION)

args = parser.parse_args()

from pi3d import Log
Log(name=None, level='DEBUG' if args.debug else 'WARNING')

from engine import PytaVSL
geometry = [int(x) for x in args.resolution.split('x')]
pyta = PytaVSL(
    name=args.namespace,
    port=args.port,
    fps=args.fps,
    # fullscreen=args.fullscreen,
    width=geometry[0],
    height=geometry[1],
    window_title=args.title,
    max_gpu_memory=args.max_vram,
    show_fps=args.show_fps,
    memtest=args.memtest
)

if args.api:
    pyta.print_api()
else:
    if args.load:
        pyta.load_textures(*args.load)
    if args.text:
        for item in args.text:
            pyta.create_text(*item.split(':'))
    pyta.start()
