import os.path

from mysound.fileformats import source
from mysound.generator import silence
from mysound.processor import mean
from mysound.actions import pick
from mysound.sink import sink

SRC_FILE = os.path.join('.', 'test', 'data', 'ping1000hz.wav')
DST_FILE = os.path.join('.', 'test', 'tmp', 'ping1000hz-mean.wav')

ctx, src = source(SRC_FILE)
src[1] = pick(100, silence(ctx), src[1])
sink(ctx, [mean(*src)], DST_FILE)

  
