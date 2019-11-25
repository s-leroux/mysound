""" A processor in `mysound` is taking 1 or several
    input signal to produce one or several output signals

    Processors can do things like resampling a signal, reproducing
    it on several channels or mixing several channels together
"""
import math

from mysound.generator import samples
from mysound.multichannel import mux

def eof(*args):
    return [], eof

def take(count, source):
    """ Take *exactly* _count_ samples from _source_
    """
    # XXX Does this really belong to this module?
    cont = source

    result = samples()
    while count > 0:
        data, cont = cont(count)
        count -= len(data)
        result.extend(data)

    return result, cont


def apply(fct, *channels):
    """ Apply a function on each samples in turn
    """

    src = mux(*channels)

    def _apply(fct, src):
        def read(n):
            chunk, cont = src(n)
            if not chunk:
                return eof()

            return samples(map(fct, zip(*chunk))), _apply(fct, cont)

        return read

    return _apply(fct, src)

def mean(*channels):
    """ Return one channel that is the arithmetic average
        of all input channels
    """
    nchannels = len(channels)
    src = mux(*channels)

    def _apply(fct, src):
        def read(n):
            chunk, cont = src(n)
            if not chunk:
                return eof()

            return samples([fct(vector)/nchannels for vector in zip(*chunk)]), _apply(fct, cont)

        return read

    return _apply(math.fsum, src)


