import importlib

from mysound.context import Context
from mysound.multichannel import mux, demux
from mysound.actions import caching

def fromFile(cls, *args):
    try:
        wav = cls(*args)
    except:
        wav.close()
        raise

    return Context(srate=wav.srate), demux(wav.nchannels, blockReader(wav))

def blockReader(wav):
    data = None
    cont = None
    loaded = False
    eof = lambda : (None, eof)

    def read(count = 4096):
        nonlocal data, cont, loaded

        if not loaded:
            data = wav.read(count)
            cont = blockReader(wav)
            loaded = True
            if not data:
                wav.close()

        if not data:
            return eof()

        return data, cont

    return read

def toFile(cls, ctx, src, *args):
    with cls(ctx.srate, 32, len(src), *args) as dst:
        src = mux(*src)
        while True:
            data, src = src(10*1024)
            if not data:
                break

            dst.write(data)

READER = {}
WRITER = {}
for fmt in ("wave","dummy"):
    module = importlib.import_module("mysound.fileformats.{}".format(fmt))
    try:
        reader = getattr(module, 'Reader', None)
        writer = getattr(module, 'Writer', None)

        if reader:
            READER[fmt.upper()] = (lambda reader : lambda *args : fromFile(reader, *args))(reader)
        if writer:
            WRITER[fmt.upper()] = (lambda writer : lambda ctx, src, *args : toFile(writer, ctx, src, *args))(writer)
    finally:
        del module

WAVE_FILE="WAVE"
def source(*args, format=WAVE_FILE):
    return READER[format](*args)
