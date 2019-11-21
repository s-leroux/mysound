""" Pure Python interface to Wave sound files

    based on http://www-mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/WAVE.html
"""

import struct

from collections import namedtuple
from types import SimpleNamespace
from array import array

INT8 = 'B'
INT32 = 'I'
INT16 = 'H'
CHAR3 = '3s'
CHAR4 = '4s'
CHAR14 = '14s'

FLOAT32 = 'f'

CHUNKS = {
  b"RIFF": (
    ( 'ckSize', INT32 ),
    ( 'WAVEID', CHAR4 ),
  ),
  b"fmt 16": (
    ( 'wFormatTag', INT16 ),
    ( 'nChannels', INT16 ),
    ( 'nSamplesPerSec', INT32 ),
    ( 'nAvgBytesPerSec', INT32 ),
    ( 'nBlockAlign', INT16 ),
    ( 'wBitsPerSample', INT16 ),
  ),
  b"fmt 18": (
    ( 'cbSize', INT16 ),
  ),
  b"fmt 40": (
    ( 'wValidBitsPerSample', INT16 ),
    ( 'dwChannelMask', INT32 ),
    ( 'wFormatTag', INT16 ),
    ( 'SubFormat', CHAR14 ),
  ),
}


PARSER={ k: struct.Struct("".join(("<", *tuple(zip(*fields))[1]))) for k, fields in CHUNKS.items() }
NTUPLE={ k: namedtuple("_", tuple(zip(*fields))[0]) for k, fields in CHUNKS.items() }
READER={ k: lambda f, k=k : NTUPLE[k](*PARSER[k].unpack(f.read(PARSER[k].size))) for k in CHUNKS }

WAVE_FORMAT_PCM = 0x0001
WAVE_FORMAT_IEEE_FLOAT = 0x0003

STEREO=2
MONO=1


def SWP24(seq):
    return ((int.from_bytes(i, 'little') for i in block) for block in seq)

_PCM_FLOAT32 = struct.Struct("<"+FLOAT32) 

import itertools
def PCM_FLOAT32(buffer, nchannels):
    channels = [array('f') for _ in range(nchannels)]
    channel = itertools.cycle(channels)
    for n, in _PCM_FLOAT32.iter_unpack(buffer):
        next(channel).append(n)
    
    return channels

def PCM_INT8(buffer, nchannels):
    channels = [array('f') for _ in range(nchannels)]
    ifb = int.from_bytes
    for n in range(0, len(buffer), nchannels):
        for c in channels:
            c.append((ifb(buffer[n:n+1], 'little')-128)/128)
            n+=1
    
    return channels

#
# According to http://blog.bjornroche.com/2009/12/int-float-int-its-jungle-out-there.html 
# there is no well defined standard for int -> flot conversion
#
# It more important though that 0 -> 0.0 rather than using the full [-1;+1] range
# A simple `/ 0x8000` (for 16 bits) is the choice made by ALSA I will follow here
#
def PCM_SIGNED_INT(buffer, bytesperchannel, nchannels):
    channels = [array('f') for _ in range(nchannels)]
    amplitude = (1<<bytesperchannel-1)
    ifb = int.from_bytes
    for n in range(0, len(buffer), nchannels*bytesperchannel):
        for c in channels:
            c.append(ifb(buffer[n:n+bytesperchannel], 'little')/amplitude)
            n+=bytesperchannel
    
    return channels

def PCM_INT8_MONO(buffer):
    return PCM_INT8(buffer, 1)

def PCM_INT8_STEREO(buffer):
    return PCM_INT8(buffer, 2)

def PCM_INT16_MONO(buffer):
    return PCM_SIGNED_INT(buffer, 2, 1)

def PCM_INT16_STEREO(buffer):
    return PCM_SIGNED_INT(buffer, 2, 2)

def PCM_INT24_MONO(buffer):
    return PCM_SIGNED_INT(buffer, 3, 1)

def PCM_INT24_STEREO(buffer):
    return PCM_SIGNED_INT(buffer, 3, 2)

def PCM_INT32_MONO(buffer):
    return PCM_SIGNED_INT(buffer, 4, 1)

def PCM_INT32_STEREO(buffer):
    return PCM_SIGNED_INT(buffer, 4, 2)

def PCM_FLOAT32_MONO(buffer):
    return PCM_FLOAT32(buffer, 1)

def PCM_FLOAT32_STEREO(buffer):
    return PCM_FLOAT32(buffer, 2)

FORMATS={
    (WAVE_FORMAT_PCM, 1, 8, MONO): PCM_INT8_MONO,
    (WAVE_FORMAT_PCM, 2, 8, STEREO): PCM_INT8_STEREO,
    (WAVE_FORMAT_PCM, 2, 16, MONO): PCM_INT16_MONO,
    (WAVE_FORMAT_PCM, 4, 16, STEREO): PCM_INT16_STEREO,
    (WAVE_FORMAT_PCM, 3, 24, MONO): PCM_INT24_MONO,
    (WAVE_FORMAT_PCM, 6, 24, STEREO): PCM_INT24_STEREO,
    (WAVE_FORMAT_PCM, 4, 32, MONO): PCM_INT32_MONO,
    (WAVE_FORMAT_PCM, 8, 32, STEREO): PCM_INT32_STEREO,
    (WAVE_FORMAT_IEEE_FLOAT, 4, 32, MONO): PCM_FLOAT32_MONO,
    (WAVE_FORMAT_IEEE_FLOAT, 8, 32, STEREO): PCM_FLOAT32_STEREO,
}

class WaveReader:
    def __init__(self, stream):
        self.state = SimpleNamespace()
        self.state.format = None
        self.state.nsamplespersec = None
        self.state.nchannels = None
        self.state.wbitspersample = None
        self.state.nblockalign = None

        self.readWaveHeader(stream)
        while True:
            ck = self.readNextChunk(stream)
            if ck is None:
                # end of stream
                break

        print(self.state)
        f = FORMATS.get((self.state.format, self.state.nblockalign, self.state.wbitspersample, self.state.nchannels), "?")
        print(stream, f)
        

    def assertTrue(self, test, msg, *args):
        if not test:
            raise TypeError(msg.format(args))

    @classmethod
    def fromFile(cls, path):
        with open(path, "rb") as f:
            return cls(f)

    def readWaveHeader(self, stream):
        magick = stream.read(4)
        self.assertTrue(magick == b"RIFF", "{} does not seem to be a valid WAV file", stream)

        header = READER[magick](stream)
        if header.WAVEID != b"WAVE":
            raise TypeError("{} does not seem to be a valid WAV file".format(stream))
        

    def readNextChunk(self, stream):
        ckID = stream.read(4)
        if not ckID:
            return None

        self.assertTrue(len(ckID) == 4, "Premature end of the WAV file")

        cksize = stream.read(4)
        self.assertTrue(len(cksize) == 4, "Premature end of the WAV file")
        cksize = int.from_bytes(cksize, 'little')

        ckHandler = self.chunkHandlers.get(ckID, self.__class__.handleUnknownChunk)
        print(ckID, ckHandler)
        ckHandler(self, stream, ckID, cksize)

        return True

    def handleUnknownChunk(self, stream, ckID, cksize):
        # skip without requiring the steam to support ftell/fseek operations
        while cksize:
            garbage = stream.read(min(cksize, 4096))
            consumed = len(garbage)
            self.assertTrue(consumed, "Premature end of the WAV file")
                
            cksize -= consumed

    def handlefmt_Chunk(self, stream, ckID, cksize):
        if cksize == 16:
            self.handlefmt_16Chunk(stream, ckID, cksize)
        elif cksize == 18:
            self.handlefmt_18Chunk(stream, ckID, cksize)
        elif cksize == 40:
            self.handlefmt_40Chunk(stream, ckID, cksize)
        else:
            raise TypeError("Invalid fmt chunk size")


    def handlefmt_16Chunk(self, stream, ckID, cksize):
        chunk16 = READER[b'fmt 16'](stream)
        self.state.format = chunk16.wFormatTag
        self.state.nchannels = chunk16.nChannels
        self.state.nsamplespersec = chunk16.nSamplesPerSec
        self.state.nblockalign = chunk16.nBlockAlign
        self.state.wbitspersample = chunk16.wBitsPerSample


    def handlefmt_18Chunk(self, stream, ckID, cksize):
        self.handlefmt_16Chunk(stream, ckID, cksize)
        chunk18 = READER[b'fmt 18'](stream)
        self.assertTrue(chunk18.cbSize == 0, "Bad data in fmt 18 chunk")

    def handlefmt_40Chunk(self, stream, ckID, cksize):
        self.handlefmt_16Chunk(stream, ckID, cksize)
        chunk18 = READER[b'fmt 18'](stream)
        self.assertTrue(chunk18.cbSize == 22, "Bad data in fmt 40 chunk")

        chunk40 = READER[b'fmt 40'](stream)
        self.state.format = chunk40.wFormatTag
    
    def handledataChunk(self, stream, ckID, cksize):
        fmt = FORMATS[self.state.format, self.state.nblockalign, self.state.wbitspersample, self.state.nchannels]
        nChannels = self.state.nchannels
        maxBufferSize = 4*self.state.nblockalign

        while cksize:
              count = min(cksize, maxBufferSize)
              buffer = stream.read(count)
              if not buffer:
                  break

              cksize -= len(buffer)
              samples = fmt(buffer)

        print(list(samples))

        self.assertTrue(cksize == 0, 'Premature end of file')

    chunkHandlers = { 
        b'fmt ': handlefmt_Chunk,
        b'data': handledataChunk,
    }


def reader():
    pass
