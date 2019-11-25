""" A collection of utilities working both
    on 1-channel and multi-channels data sources
"""

def loop(source):
    """ Repeat forever the same source of data
    """
    def _loop(curr):
        def read(count):
            data, cont = curr(count)
            if not data:
                data, cont = source(count)

            return data, _loop(cont)

        return read

    return _loop(source)

def pick(n, first, second):
    """ Read up to n data from the first source, then switch to the
        second one.
    """

    def read(count):
        if n <= 0:
            return second(count)

        if n < count:
            count = n

        data, cont = first(count)
        return data, pick(n-len(data), cont, second)

    return read

def caching(source):
    """ This function cache (memoize) data from
        a source. It is mostly useful to avoid
        recalculation for computationaly expensive
        processors, or when working with stateful
        or otherwise non-idempotent data source
    """
    cache = None
    cont = None
    loaded = False

    def at(offset):
        def read(count):
            nonlocal cache, cont, loaded
            if not loaded:
                cache, cont = source(count)
                cont = caching(cont)
                loaded = True

            stop = offset+count
            if stop >= len(cache):
                return cache[offset:], cont

            return cache[offset:stop], at(stop)


        return read

    return at(0)
