from obspy.core.util.attribdict import AttribDict
from obspy import Stream, Trace, UTCDateTime
import numpy as np
import struct

def readstructtag(fid):
    y = AttribDict()
    y.sinc, y.machine, y.id_struct, y.len_struct, y.len_data = struct.unpack("BBhii", fid.read(12))
    return y


def readdescripttrace(fid):
    y = AttribDict()
    y.network = "".join(["%s" % chr(_) for _ in struct.unpack("BBBB", fid.read(4))]) # char(fread(fid, 4, 'uchar'))
    y.st_name = "".join(["%s" % chr(_) for _ in struct.unpack("BBBBB", fid.read(5))])  # char(fread(fid, 5, 'uchar'))
    y.component = chr(struct.unpack("B", fid.read(1))[0]) # char(fread(fid, 1, 'uchar'))
    y.insstype = struct.unpack("h", fid.read(2))[0] # fread(fid, 1, 'int16')
    y.begintime =  struct.unpack("d", fid.read(8))[0] # fread(fid, 1, 'double')
    y.localtime =  struct.unpack("h", fid.read(2))[0] # fread(fid, 1, 'int16')
    y.datatype = chr(struct.unpack("B", fid.read(1))[0]) # char(fread(fid, 1, 'uchar'))
    y.descriptor = chr(struct.unpack("B", fid.read(1))[0])  # char(fread(fid, 1, 'uchar'))
    y.digi_by = struct.unpack("h", fid.read(2))[0]  # fread(fid, 1, 'int16')
    y.processed = struct.unpack("h", fid.read(2))[0]  # fread(fid, 1, 'int16')

    y.length = struct.unpack("i", fid.read(4))[0]  # fread(fid, 1, 'int32')
    y.rate =  struct.unpack("f", fid.read(4))[0]  # fread(fid, 1, 'float32')
    y.mindata = struct.unpack("f", fid.read(4))[0]  # fread(fid, 1, 'float32')
    y.maxdata = struct.unpack("f", fid.read(4))[0]  # fread(fid, 1, 'float32')
    y.avenoise = struct.unpack("f", fid.read(4))[0]  # fread(fid, 1, 'float32')
    y.numclip = struct.unpack("i", fid.read(4))[0]  # fread(fid, 1, 'int32')
    y.timecorrect = struct.unpack("d", fid.read(8))[0] # fread(fid, 1, 'double')
    y.rate_correct = struct.unpack("f", fid.read(4))[0]  # fread(fid, 1, 'float32')
    return y

def readdata(fid, n, t):
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
    target = types[t]
    return struct.unpack(target[1] * n, fid.read(n*target[2]))


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

def _read_dmx(filename, head_only=None, **kwargs):
    traces = []
    with open(filename, "rb") as fid:
        while fid.read(12): # we require at least 1 full structtag
            fid.seek(-12, 1)
            structtag = readstructtag(fid)
            if structtag.id_struct == 7:
                descripttrace = readdescripttrace(fid)
                data = readdata(fid, descripttrace.length, descripttrace.datatype)
                tr = Trace(data=np.asarray(data))
                tr.stats.network = descripttrace.network.rstrip('\x00').rstrip(' ')
                tr.stats.station = descripttrace.st_name.rstrip('\x00').rstrip(' ')
                tr.stats.channel = descripttrace.component.rstrip('\x00').rstrip(' ')
                tr.stats.sampling_rate = descripttrace.rate
                tr.stats.starttime = UTCDateTime(descripttrace.begintime)
                tr.stats.dmx = {**descripttrace, **structtag}
                traces.append(tr)
            else:
                fid.seek(int(structtag.len_struct) + int(structtag.len_data), 1)
    st = Stream(traces=traces)
    return st

