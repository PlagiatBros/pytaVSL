# encoding: utf-8

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from sys import argv
from . import __version__

parser = ArgumentParser(prog="python3 %s" % argv[0], formatter_class=ArgumentDefaultsHelpFormatter)

parser.add_argument('--namespace', help='osc namespace', default='pyta')
parser.add_argument('--port', help='udp port or unix socket path', default=5555)
parser.add_argument('--load', help='image files to load', nargs='+', metavar='FILES')
parser.add_argument('--text', help='text objects to create', nargs='+', metavar='NAME:FONT', default=["0:sans", "1:sans", "2:mono", "3:mono"])
parser.add_argument('--scenes', help='scene files to load', nargs='+', metavar='FILES')
parser.add_argument('--fps',  help='maximum framerate, 0 for free wheeling', type=int, default=25)
parser.add_argument('--precompile',  help='precompile effect shaders at startup', default=False, action='store_true')
parser.add_argument('--max-vram',  help='maximum video memory allocation (in MB)', type=int, default=64)
parser.add_argument('--memtest',  help='test video memory size', default=False, action='store_true')
parser.add_argument('--fullscreen',  help='launch in fullscreen', default=False, action='store_true')
parser.add_argument('--api',  help='print osc api and exit', default=False, action='store_true')
parser.add_argument('--debug',  help='print debug logs', default=False, action='store_true')
parser.add_argument('--show-fps',  help='show fps', default=False, action='store_true')
parser.add_argument('--resolution',  help='output resolution', type=str, default='800x600', metavar='WIDTHxHEIGHT')
parser.add_argument('--title',  help='window title', type=str, default='pytaVSL', metavar='TITLE')
parser.add_argument('--audio',  help='enable audio playback of video slides (when visible)', default=False, action='store_true')
parser.add_argument('--jack',  help='use jack backend for audio playback', default=False, action='store_true')
parser.add_argument('--version', action='version', version=__version__)

config = parser.parse_args()
