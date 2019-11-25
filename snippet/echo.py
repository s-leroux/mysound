import os.path

from mysound.generator import source, silence
from mysound.processor import pick
from mysound.sink import sink

SRC_FILE = os.path.join('.', 'test', 'data', 'ping1000hz.wav')
DST_FILE = os.path.join('.', 'test', 'tmp', 'ping1000hz-echo.wav')

ctx, src = source(SRC_FILE)
src[1] = pick(ctx, 100, silence(ctx), src[1])
sink(ctx, src, DST_FILE)

  
