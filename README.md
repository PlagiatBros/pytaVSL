## pytaVSL
*python tiny approximative Virtual Stage Light*

pytaVSL is a video-projection and compositing software built on top of [pi3d](https://github.com/tipam/pi3d/). It's designed for the live and has many cool features:
- fully osc-controllable
- slides (from image, gif and video files)
- texts (rendered using signed distance fields)
- per slide/text settings, effects, mapping, animations and states
- slide groups (with effects, animations, etc)
- global scenes management

### Requirements

- python3
- python3-liblo
- python3-toml
- python3-opencv (if video playback is needed)
- [pi3d](https://github.com/tipam/pi3d/)


### Usage

```
usage: python3 ./pytaVSL.py [-h] [--namespace NAMESPACE] [--port PORT]
                            [--load FILES [FILES ...]]
                            [--text NAME:FONT [NAME:FONT ...]]
                            [--scenes FILES [FILES ...]] [--fps FPS]
                            [--precompile] [--max-vram MAX_VRAM] [--memtest]
                            [--fullscreen] [--api] [--debug] [--show-fps]
                            [--resolution WIDTHxHEIGHT] [--title TITLE]
                            [--version]

optional arguments:
  -h, --help            show this help message and exit
  --namespace NAMESPACE
                        osc namespace (default: pyta)
  --port PORT           udp port or unix socket path (default: 5555)
  --load FILES [FILES ...]
                        image files to load (default: None)
  --text NAME:FONT [NAME:FONT ...]
                        text objects to create (default: ['0:sans', '1:sans',
                        '2:mono', '3:mono'])
  --scenes FILES [FILES ...]
                        scene files to load (default: None)
  --fps FPS             maximum framerate, 0 for free wheeling (default: 25)
  --precompile          precompile effect shaders at startup (default: False)
  --max-vram MAX_VRAM   maximum video memory allocation (in MB) (default: 64)
  --memtest             test video memory size (default: False)
  --fullscreen          launch in fullscreen (default: False)
  --api                 print osc api and exit (default: False)
  --debug               print debug logs (default: False)
  --show-fps            show fps (default: False)
  --resolution WIDTHxHEIGHT
                        output resolution (default: 800x600)
  --title TITLE         window title (default: pytaVSL)
  --version             show program's version number and exit
```

### Documentation

The osc api can be read [here](https://github.com/PlagiatBros/pytaVSL/blob/master/API) or by running the following command:
```
python3 pytaVSL.py --api | less -cr
```

###  License

Copyleft © 2019 Plagiat Brother; Original Code © Aurélien Roux; based upon Virtual Stage Light by Gregory David.
This program is a free software released under the [GNU/GPL3](https://github.com/PlagiatBros/pytaVSL/blob/master/LICENSE) license.

**Included Fonts**

- League Gothic © Caroline Hadilaksono, Micah Rich, & Tyler Finck / Open Font License
- FreeMono © Free Software Foundation / GNU GPLv3
