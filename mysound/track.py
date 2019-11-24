
def eof(*args):
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
