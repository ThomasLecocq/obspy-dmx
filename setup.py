from setuptools import setup, find_packages
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
    url='https://github.com/ThomasLecocq/obspy-dmx',
    description='ObsPy reader for DMX format (INGV)',
    long_description='',
    entry_points=ENTRY_POINTS,
    zip_safe=False,
    packages=find_packages(),
    include_package_data=True,
    # packages=['obspy_dmx', 'obspy_dmx.tests', 'obspy_dmx.tests.data'],
    # package_data={'obspy_dmx': ['obspy_dmx/tests/data/*.*']},
)
