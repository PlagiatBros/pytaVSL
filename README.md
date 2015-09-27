pytaVSL
=======

pytaVSL stands for python tiny alpproximative VSL. 
It's a VJing and lights-projector virtualization program using pi3d, and aimed to reproduce some of the features one could find in the pd-patches set called VSL. The final destination arch of pytaVSL is the Raspberry PI.

Copyright
=========

Copyright (C) 2014 Aurélien Roux <orl@ammd.net> - based upon Virtual Stage Light by Gregory David <groolot@groolot.net>

http://ammd.net/-DIY-

License
=======

pytaVSL is released under the terms of the GNU General Public License, version 2 or later. 

Dependencies
============

- python-liblo
- pi3d

Classes
=======

Slide
-----

A plane in the 3D space, which might be textured with image.

Container
---------

A set of slides in which the textured images will be displayed.

PytaVSL
-------

The main class, it contains the OSC server and methods, the 3D Display, the Shader, the Camera, the files list, and the Containers.
