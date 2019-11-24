""" A processor in `mysound` is taking 1 or several
    input signal to produce one or several output signals

    Processors can do things like resampling a signal, reproducing
    it on several channels or mixing several channels together
"""

def loop(signal):
    """ A processor that repeats forever the same signal
    """
    def y(curr):
        def generator(n):
            samples, f = curr(n)
            if not samples:
                samples, f = signal(n)

            return samples, y(f)

        return generator

    return y(signal)

def pick(context, n, first, second):
    """ Pick n samples from the first signal, then switch to the
        second one
    """

    def generator(count):
        if n <= 0:
            return second(count)

        if n < count:
            count = n

        data, cont = first(count)
        return data, pick(context, n-len(data), cont, second)

    return generator
