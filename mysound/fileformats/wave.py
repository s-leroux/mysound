""" Pure Python interface to Wave sound files

    based on http://www-mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/WAVE.html
"""

import struct

from collections import namedtuple

INT32 = 'I'
INT16 = 'H'
CHAR4 = '4s'
CHAR14 = '14s'

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
    ( 'SubFormat_0', INT16 ),
    ( 'SubFormat_1', CHAR14 ),
  ),
}


PARSER={ k: struct.Struct("".join(("<", *tuple(zip(*fields))[1]))) for k, fields in CHUNKS.items() }
NTUPLE={ k: namedtuple("_", tuple(zip(*fields))[0]) for k, fields in CHUNKS.items() }
READER={ k: lambda f, k=k : NTUPLE[k](*PARSER[k].unpack(f.read(PARSER[k].size))) for k in CHUNKS }

class WaveReader:
    def __init__(self, stream):
        self.readWaveHeader(stream)
        while True:
            ck = self.readNextChunk(stream)
            if ck is None:
                # end of stream
                break

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
        if ckHandler == b'DATA':
            return stream, cksize # yield?
        else:
            ckHandler(self, stream, ckID, cksize)

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

    def handlefmt_18Chunk(self, stream, cksize):
        chunk16 = READER[b'fmt 16'](stream)
        chunk18 = READER[b'fmt 18'](stream)
        self.assertTrue(chunk18.cbSize == 0, "Bad data in fmt 18 chunk")

    def handlefmt_40Chunk(self, stream, ckID, cksize):
        chunk16 = READER[b'fmt 16'](stream)
        chunk18 = READER[b'fmt 18'](stream)
        self.assertTrue(chunk18.cbSize == 22, "Bad data in fmt 40 chunk")
        chunk40 = READER[b'fmt 40'](stream)
        

    chunkHandlers = { 
        b'fmt ': handlefmt_Chunk,
    }


def reader():
    pass
