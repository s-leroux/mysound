from mysound.fileformats import WRITER

WAVE_FILE="WAVE"
def sink(ctx, *args, format=WAVE_FILE):
    return WRITER[format](ctx, *args)

