from setuptools import setup, find_packages
from sys import path

path.insert(0, './')

from pytaVSL import __version__

setup(
    name='pytaVSL',
    packages=['pytaVSL', 'pytaVSL.engine', 'pytaVSL.fonts', 'pytaVSL.shaders', 'pytaVSL.slides'],
    package_data={'pytaVSL': ['shaders/*', 'shaders/**/*', 'fonts/*']},
    version=__version__,
    description='python tiny aproximative Virtual Stage Light',
    url='https://github.com/PlagiatBros/pytaVSL',
    author='Plagiat Brothers',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
    ],
    python_requires='>=3',
    install_requires=[
        'pi3d==2.36',
        'toml==0.10',
        'liblo==0.10'
    ],
    extras_require={
        'video': ['opencv-python'],
        'video_audio': ['opencv-python', 'mplayer.py']
    }
)