import os.path

from mysound.generator import source
from mysound.sink import sink

SRC_FILE = os.path.join('.', 'test', 'data', 'ping1000hz.wav')
DST_FILE = os.path.join('.', 'test', 'tmp', 'ping1000hz-mono.wav')

ctx, src = source(SRC_FILE)
sink(ctx, src[:1], DST_FILE)

  
