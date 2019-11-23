
def tracks(*generators):
    """ Given a list of generators, return a function that
        can read n sample on each track simultaneously.
    """
    def _tracks(gb):
        def read(count):
            # Force loading of the first data segement. This should be idempotent.
            nonlocal gb
            gb = [ (offset,data,gen) if offset < len(data) else ( 0, *gen(count) ) for offset, data, gen in gb ]
            
            # find the shorted segment
            for t in gb:
                dataLength = len(t[1])-t[0]

                if dataLength < count:
                    count = dataLength

            data = [ data[offset:offset+count] for offset, data, gen in gb ]
            return data, _tracks([
                (offset+count, data, gen) for offset, data, gen in gb
            ])

        return read

    return _tracks([(0, [], generator) for generator in generators])
