#!/usr/bin/python3
# encoding: utf-8

from sys import path, version_info, exit

if version_info[0] != 3:
    print('Error: Python 3 is required to run pytaVSL')
    exit(0)


if __package__ == '':
    # load local package
    path.insert(0, './')

from pytaVSL.engine.core import PytaVSL
from pytaVSL.config import config


from pi3d import Log
Log(name=None, level='DEBUG' if config.debug else 'INFO')

geometry = [int(x) for x in config.resolution.split('x')]

audio = False
if config.audio:
    audio = True
    if config.jack:
        audio = 'jack'

pyta = PytaVSL(
    name=config.namespace,
    port=config.port,
    fps=config.fps,
    fullscreen=config.fullscreen,
    width=geometry[0],
    height=geometry[1],
    window_title=config.title,
    max_gpu_memory=config.max_vram,
    show_fps=config.show_fps,
    memtest=config.memtest,
    precompile_shaders=config.precompile,
    audio=audio
)

if config.memtest and 'y' not in input('Warning: the memory test may freeze/crash your system, continue ? (y/N)').lower():
    exit(0)

if config.api:
    pyta.print_api()
else:
    if config.load:
        pyta.load_textures(*config.load)
    if config.scenes:
        pyta.scenes_import(*config.scenes)
    if config.text:
        for item in config.text:
            pyta.create_text(*item.split(':'))
    pyta.start()
