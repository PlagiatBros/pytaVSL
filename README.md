## pytaVSL
*python tiny approximative Virtual Stage Light*


### Requirements

- python
- python-liblo
- [pi3d](http://pi3d.github.io)


### Usage

```
usage: python ./pytaVSL.py [-h] [--name NAME] [--port PORT]
                           [--load FILES [FILES ...]] [--fps FPS]
                           [--max-gpu MAX_GPU] [--fullscreen] [--api]
                           [--log {debug,info,warning,error,critical}]

optional arguments:
  -h, --help            show this help message and exit
  --name NAME           osc namespace (default: pyta)
  --port PORT           udp port or unix socket path (default: 5555)
  --load FILES [FILES ...]
                        image files to load (default: None)
  --fps FPS             maximum framerate (default: 25)
  --max-gpu MAX_GPU     maximum gpu memory (in MB) (default: 64)
  --fullscreen          launch in fullscreen (default: False)
  --api                 print osc api and exit (default: False)
  --log {debug,info,warning,error,critical}
                        verbosity level (default: warning)
```

###  License

Copyleft © 2019 Plagiat Brother; Original Code © Aurélien Roux; based upon Virtual Stage Light by Gregory David.
This program is a free software released under the [GNU/GPL3](https://github.com/PlagiatBros/pytaVSL/blob/master/LICENSE) license.

Included fonts: leaguegothic (sans), freemono (mono)
