import importlib

from mysound.context import Context

def caching(reader):
    cache = None
    cont = None
    loaded = False

    def read(count):
        nonlocal cache, cont, loaded

        if not loaded:
            cache, cont = reader(count)
            cont = caching(cont)
            loaded = True

        return cache, cont

    return read

def multichannel(count, reader):
    def channel(n, reader, offset, cache, cont):
        loaded = False

        def read(count):
            nonlocal cache, loaded, cont

            if not loaded:
                block, cont = reader()
                cache = block[n] if block else []
                loaded = True

            remaining = len(cache)-offset
            if remaining < count:
                count = remaining

            stop = offset+count
            data = cache[offset:stop]

            if count == remaining:
                return data, channel(n, cont, 0, None, None)
            else:
                return data, channel(n, reader, stop, cache, cont)

        return read

    return [channel(n, reader, 0, None, None) for n in range(count)]

def fromFile(cls, *args):
    try:
        wav = cls(*args)
    except:
        wav.close()
        raise

    return Context(srate=wav.srate), multichannel(wav.nchannels, blockReader(wav))

def blockReader(wav):
    data = None
    cont = None
    loaded = False
    eof = lambda : (None, eof)

    def read():
        nonlocal data, cont, loaded

        if not loaded:
            data = wav.read(4096)
            cont = blockReader(wav)
            loaded = True
            if not data:
                wav.close()

        if not data:
            return eof()

        return data, cont

    return read

from mysound.track import mux
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

