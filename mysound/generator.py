""" Sound generators

   In _mysound_, `generators` are the source of all sound samples.
   Generators can produce samples algorithmically, or by reading
   them from an external source (typically, a sound file)

   Generators can be combined to produce higher oorder generators.
   This is the basic way of processing sounds with `mysound`
"""

from array import array

from mysound.time import to_samples, seconds
from mysound.fileformats import READER

MIN = -1.0
MAX = 1.0
ZERO = 0.0

def y(context, f):
    r = lambda *args : (f(*args), y(context, f))
    r.context = context

    return r

def sample(*values):
    return array('f', values)

def silence(context):
    """ Return a generator producing an infinite amount of silence
    """
    return constant(context, ZERO)

def constant(context, v):
    """ Return a generator producing an infinite stream of samples
        with the same value
    """
    buffer = sample(v)*1000

    def generator(n):
        return buffer[:n]

    return y(context, generator)

def ramp(ctx, duration=seconds(1), start=MIN, stop=MAX):
    """ Return a genertor that walks up through the [from, to] range
        (inclusive) in _duration_. The duration is expressed in samples
        or using any of the `mysound.time` formats.

        The actual number of samples in a ramp is dependant of the
        `context.srate`
    """
    count = to_samples(ctx, duration)
    amplitude = float(stop-start)

    def y(start, amplitude, acc, count):
        def generator(n):
            n = min(n, count-acc)
            r = sample(0)*n

            i = 0
            while i < n:
                r[i] = start + (acc+i)/(count-1)*amplitude
                i += 1

            return r, y(start, amplitude, acc+i, count)

        return generator

    return y(float(start), amplitude, 0, count)

WAVE_FILE="WAVE"
def source(*args, format=WAVE_FILE):
    return READER[format](*args)
