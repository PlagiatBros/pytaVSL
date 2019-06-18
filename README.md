## pytaVSL
*python tiny approximative Virtual Stage Light*


### Requirements

- python3
- python3-liblo
- python3-toml
- [pi3d](http://pi3d.github.io)


### Usage

```
usage: python ./pytaVSL.py [-h] [--namespace NAMESPACE] [--port PORT]
                           [--load FILES [FILES ...]]
                           [--text NAME:FONT [NAME:FONT ...]] [--fps FPS]
                           [--max-gpu MAX_GPU] [--fullscreen] [--api]
                           [--debug] [--show-fps] [--geometry WIDTHxHEIGHT]
                           [--title TITLE] [--version]

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
  --fps FPS             maximum framerate, 0 for free wheeling (default: 25)
  --max-gpu MAX_GPU     maximum gpu memory (in MB) (default: 64)
  --api                 print osc api and exit (default: False)
  --debug               print debug logs (default: False)
  --show-fps            show fps (default: False)
  --geometry WIDTHxHEIGHT
                        output resolution (default: 800x600)
  --title TITLE         window title (default: pytaVSL)
  --version             show program's version number and exit
```

### Documentation

The osc api can be read by running the following command:
```
python3 pytaVSL.py --api | less -cr
```

###  License

Copyleft © 2019 Plagiat Brother; Original Code © Aurélien Roux; based upon Virtual Stage Light by Gregory David.
This program is a free software released under the [GNU/GPL3](https://github.com/PlagiatBros/pytaVSL/blob/master/LICENSE) license.

**Included Fonts**

- League Gothic © Caroline Hadilaksono, Micah Rich, & Tyler Finck / Open Font License
- FreeMono © Free Software Foundation / GNU GPLv3
