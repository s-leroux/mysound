""" A sink is a consumer for a list of channels. All streams
    are read in sync and samples are consumed until at least one
    channel is exhausted.
"""


from mysound.fileformats import WRITER

WAVE_FILE="WAVE"
def sink(ctx, *args, format=WAVE_FILE):
    return WRITER[format](ctx, *args)

