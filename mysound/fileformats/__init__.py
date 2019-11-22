import importlib

from mysound.context import Context

READER = {}

def fromFile(cls, path):
    wav = None
    eof = lambda : (None, eof)
    reader = None

    try:
        wav = cls(open(path, "rb"))
    except:
        wav.close()
        raise

    def _reader(count):
        data = wav.read(count)
        if not data:
            wav.close()
            return eof()
        
        return data, reader

    reader = _reader
    return Context(srate=wav.srate), reader

for fmt in ("wave",):
    module = importlib.import_module("mysound.fileformats.{}".format(fmt))
    READER[fmt.upper()] = lambda path : fromFile(module.Reader, path)

    del module

