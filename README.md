# obspy-dmx
INGV DMX reader (to be added to obspy, already functionnal but no complete test suite)

This reader is based on the Matlab version by Andrea Cannata, rewritten to use Numpy's fromfile method for efficiency.

## Installation

After installing obspy, simply:

``pip install https://github.com/ThomasLecocq/obspy-dmx/archive/master.zip``

And this code will declare its entry points to ObsPy.

## Usage

Because this code declared its entry points, one can use ObsPy's ``read`` method like for any other format:

```python
from obspy import read
st = read("/path/to/dmx/archive/2019/20190101/*.DMX")
```

Or, for more efficiency:

```python
from obspy import read
st = read("/path/to/dmx/archive/2019/20190101/*.DMX", format="DMX")
```

The code also supports only returning one station:

```python
from obspy import read
st = read("/path/to/dmx/archive/2019/20190101/*.DMX", format="DMX", station="ABC")
```

