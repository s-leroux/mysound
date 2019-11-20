""" By default, all duration in `mysound` are expressed in samples.
    Of course, when counting in samples, the real duration is dependent
    of the sampling rate.
    This module contains utilities to use clock-wall durations that will
    be converted to samples based on the current context. 
"""

def to_samples(ctx, duration):
    """ Convert a duration in a number of samples if the given context
    """
    if callable(duration):
        duration = duration(ctx)
    
    assert isinstance(duration, int), "Sample count must be expressed as integers"
    assert duration >= 0, "Sample count must be positive"
    return duration

    return duration._to_samples(ctx)

def seconds(n):
    return lambda ctx : int(ctx.srate*n)

def samples(n):
    return lambda ctx : n

def hms(hours_, minutes_, seconds_):
    return seconds(3600*hours_+60*minutes_+seconds_)
