""" A processor in `mysound` is taking 1 or several
    input signal to produce one or several output signals

    Processors can do things like resampling a signal, reproducing
    it on several channels or mixing several channels together
"""
from mysound.generator import samples

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
