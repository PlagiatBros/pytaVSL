from setuptools import setup, find_packages

from pytaVSL import __version__

setup(
    name='pytaVSL',
    packages=['pytaVSL', 'pytaVSL.engine', 'pytaVSL.fonts', 'pytaVSL.shaders', 'pytaVSL.slides'],
    package_data={'pytaVSL': ['shaders/**/*', 'fonts/*']},
    version=__version__,
    description='python tiny aproximative Virtual Stage Light',
    url='https://github.com/PlagiatBros/pytaVSL',
    author='Plagiat Brothers',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
    ],
    python_requires='>=3'

)
