""" A context is a simple structure holding
    the various parameters for a sound, notably
    the sampling frequency.
"""

from collections import namedtuple

Context = namedtuple('Context', ['srate'])

