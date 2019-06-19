from setuptools import setup
import sys
import setuptools

__version__ = '0.0.1'

ENTRY_POINTS = {
    'obspy.plugin.waveform': [
        'DMX = obspy_dmx.core',],
    'obspy.plugin.waveform.DMX': [
        'isFormat = obspy_dmx.core:_is_dmx',
        'readFormat = obspy_dmx.core:_read_dmx',
        ],
}

setup(
    name='obspy_dmx',
    version=__version__,
    author='Thomas Lecocq & ...',
    author_email='thomas.lecocq@seismology.be',
    url='https://github.com/ThomasLecopcq/obspy-dmx',
    description='ObsPy reader for DMX format (INGV)',
    long_description='',
    entry_points=ENTRY_POINTS,
    zip_safe=True,
)
