""" Sound generators

   In _mysound_, `generators` are the source of all sound samples.
   Generators can produce samples algorithmically, or by reading
   them from an external source (typically, a sound file)

   Generators can be combined to produce higher oorder generators.
   This is the basic way of processing sounds with `mysound`
"""

from array import array

MIN = -1.0
MAX = 1.0
ZERO = 0.0

def y(f):
    return lambda *args : (f(*args), y(f))

def sample(v):
    return array('f', [v])

def silence():
    """ Return a generator producing an infinite amount of silence
    """
    return constant(ZERO)

def constant(v):
    """ Return a generator producing an infinite stream of samples
        with the same value
    """
    buffer = sample(v)*1000

    def generator(n):
        return buffer[:n] 

    return y(generator)

