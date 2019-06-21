from obspy.core.util.attribdict import AttribDict
from obspy import Stream, Trace, UTCDateTime
import numpy as np
import struct
import io

descript_trace_dtypes = np.dtype([('network', "4S"),
                       ("st_name", "5S"),
                       ("component", "1S"),
                       ("insstype", np.int16),
                       ("begintime", np.double),
                       ("localtime", np.int16),
                       ("datatype", "1S"),
                       ("descriptor", "1S"),
                       ("digi_by", np.int16),
                       ("processed", np.int16),
                       ("length", np.int32),
                       ("rate", np.float32),
                       ("mindata", np.float32),
                       ("maxdata", np.float32),
                       ("avenoise", np.float32),
                       ("numclip", np.int32),
                       ("timecorrect", np.double),
                       ("rate_correct", np.float32),
                       ])

structtag_dtypes = np.dtype([("sinc", "1S"),
                             ("machine", "1S"),
                             ("id_struct", np.int16),
                             ("len_struct", np.int32),
                             ("len_data", np.int32)])

types = {}
types["s"] = ("uint16", "H", 2)
types["q"] = ("int16", "h", 2)
types["u"] = ("uint16", "H", 2)
types["i"] = ("int16", "h", 2)
types["2"] = ("int32", "i", 4)
types["l"] = ("int32", "i", 4)
types["r"] = ("uint16", "H", 2)
types["f"] = ("float32", "f", 4)
types["d"] = ("float64", "d", 8)

def readstructtag(fid):
    y = AttribDict()
    data = np.fromfile(fid, structtag_dtypes, 1)
    for (key, (format,size)) in structtag_dtypes.fields.items():
        if str(format).count("S") != 0:
            y[key] = data[key][0].decode('UTF-8')
        else:
            y[key] = data[key][0]
    return y


def readdescripttrace(fid):
    y = AttribDict()

    data = np.fromfile(fid, descript_trace_dtypes, 1)

    for (key, (format,size)) in descript_trace_dtypes.fields.items():
        if str(format).count("S") != 0:
            y[key] = data[key][0].decode('UTF-8')
        else:
            y[key] = data[key][0]

    return y

def readdata(fid, n, t):
    target = types[t]
    return np.fromfile(fid, eval("np.%s"%target[0]), n)


def _is_dmx(filename):
    traces = []
    try:
        with open(filename, "rb") as fid:
            while fid.read(12):  # we require at least 1 full structtag
                fid.seek(-12, 1)
                structtag = readstructtag(fid)
                if structtag.id_struct == 7:
                    descripttrace = readdescripttrace(fid)
                    UTCDateTime(descripttrace.begintime)
                    return True
                else:
                    fid.seek(
                        int(structtag.len_struct) + int(structtag.len_data), 1)

    except Exception:
        return False
    return True

from tempfile import SpooledTemporaryFile

def _read_dmx(filename, head_only=None, **kwargs):
    station = None
    if "station" in kwargs:
        station = kwargs["station"]

    traces = []
    with open(filename, "rb") as fid:
        content = fid.read()

    with SpooledTemporaryFile(mode='w+b') as fid:
        fid.write(content)
        fid.seek(0)

        while fid.read(12): # we require at least 1 full structtag
            fid.seek(-12, 1)
            structtag = readstructtag(fid)
            if structtag.id_struct == 7:
                descripttrace = readdescripttrace(fid)
                if station is None or descripttrace.st_name.strip() == station:
                    data = readdata(fid, descripttrace.length,
                                    descripttrace.datatype)
                    tr = Trace(data=np.asarray(data))
                    tr.stats.network = descripttrace.network.strip()
                    tr.stats.station = descripttrace.st_name.strip()
                    tr.stats.channel = descripttrace.component
                    tr.stats.sampling_rate = descripttrace.rate
                    tr.stats.starttime = UTCDateTime(descripttrace.begintime)
                    tr.stats.dmx = AttribDict({"descripttrace":descripttrace,
                                               "structtag":structtag})
                    traces.append(tr)
                else:
                    fid.seek(int(structtag.len_data), 1)
            else:
                fid.seek(int(structtag.len_struct) + int(structtag.len_data), 1)

    st = Stream(traces=traces)
    # print(st)
    return st

