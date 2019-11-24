""" Collection of utilities to work with
    multichannel source and destinations
"""

import mysound.generator as generator

def eof(*args):
    """ Infinite generator of the `None` constant. 
        Returned when a multichannels source is exhausted;
    """
    return None, eof

def mux(*generators):
    """ Multiplex several sources to produce a multichannel source.

        When called, the multichannel source return either a n-m
        matrix of samples containing the next chunk of samples _or_
        `None` if at least one stream is exhausted.
    """
    def _mux(gb):
        def read(count):
            # Force loading of the first data segement. This should be idempotent.
            nonlocal gb
            gb = [ (offset,data,gen) if offset < len(data) else ( 0, *gen(count) ) for offset, data, gen in gb ]

            # find the shorted segment
            for t in gb:
                dataLength = len(t[1])-t[0]

                if dataLength < count:
                    count = dataLength

            if count == 0:
                # At least one stream exhausted
                return eof()

            data = [ data[offset:offset+count] for offset, data, gen in gb ]
            return data, _mux([
                (offset+count, data, gen) for offset, data, gen in gb
            ])

        return read

    return _mux([(0, [], generator) for generator in generators])

def demux(count, source):
    """ Demux a multi-channel source.
    
        Return a list of _count_ individual channels.
    """
    def channel(n, source, offset, cache, cont):
        loaded = False

        def read(count):
            nonlocal cache, loaded, cont

            if not loaded:
                block, cont = source(count)
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
                return data, channel(n, source, stop, cache, cont)

        return read

    return [channel(n, source, 0, None, None) for n in range(count)]

def rawdata(*data):
    """ Create a multichannel source from hard-coded data. Mostly used for
        testing purposes.
    """
    l = None
    for channel in data:
        chl = len(channel)
        if l != chl:
            if l is None:
                l = chl
            else:
                raise TypeError("All channels in an hardcoded multichannel data must have the same length")

    return mux(*[generator.rawdata(d) for d in data])
