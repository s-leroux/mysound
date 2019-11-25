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

WAVE_FORMAT_PCM = 0x0001
WAVE_FORMAT_IEEE_FLOAT = 0x0003
WAVE_FORMAT_EXTENSIBLE = 0xFFFE

STEREO=2
MONO=1

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
  b"fact": (
    ( 'dwSampleLength', INT32 ),
  ),
}


PARSER={ k: struct.Struct("".join(("<", *tuple(zip(*fields))[1]))) for k, fields in CHUNKS.items() }
NTUPLE={ k: namedtuple("_", tuple(zip(*fields))[0]) for k, fields in CHUNKS.items() }
READER={ k: lambda f, k=k : NTUPLE[k](*PARSER[k].unpack(f.read(PARSER[k].size))) for k in CHUNKS }


def SWP24(seq):
    return ((int.from_bytes(i, 'little', signed=True) for i in block) for block in seq)

_IEEE_FLOAT32 = struct.Struct("<"+FLOAT32)

import itertools
def IEEE_FLOAT32_DECODER(buffer, nChannels):
    channels = [array('f') for _ in range(nChannels)]
    channel = itertools.cycle(channels)
    for n, in _IEEE_FLOAT32.iter_unpack(buffer):
        next(channel).append(n)

    return channels

def PCM_INT8_DECODER(buffer, nChannels):
    channels = [array('f') for _ in range(nChannels)]
    ifb = int.from_bytes
    for n in range(0, len(buffer), nChannels):
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
def PCM_SIGNED_INT_DECODER(buffer, bytesperchannel, nChannels):
    channels = [array('f') for _ in range(nChannels)]
    amplitude = (1<<bytesperchannel*8-1)
    ifb = int.from_bytes
    for n in range(0, len(buffer), nChannels*bytesperchannel):
        for c in channels:
            c.append(ifb(buffer[n:n+bytesperchannel], 'little', signed=True)/amplitude)
            n+=bytesperchannel

    return channels

def PCM_INT8_MONO_DECODER(buffer):
    return PCM_INT8_DECODER(buffer, 1)

def PCM_INT8_STEREO_DECODER(buffer):
    return PCM_INT8_DECODER(buffer, 2)

def PCM_INT16_MONO_DECODER(buffer):
    return PCM_SIGNED_INT_DECODER(buffer, 2, 1)

def PCM_INT16_STEREO_DECODER(buffer):
    return PCM_SIGNED_INT_DECODER(buffer, 2, 2)

def PCM_INT24_MONO_DECODER(buffer):
    return PCM_SIGNED_INT_DECODER(buffer, 3, 1)

def PCM_INT24_STEREO_DECODER(buffer):
    return PCM_SIGNED_INT_DECODER(buffer, 3, 2)

def PCM_INT32_MONO_DECODER(buffer):
    return PCM_SIGNED_INT_DECODER(buffer, 4, 1)

def PCM_INT32_STEREO_DECODER(buffer):
    return PCM_SIGNED_INT_DECODER(buffer, 4, 2)

def IEEE_FLOAT32_MONO_DECODER(buffer):
    return IEEE_FLOAT32_DECODER(buffer, 1)

def IEEE_FLOAT32_STEREO_DECODER(buffer):
    return IEEE_FLOAT32_DECODER(buffer, 2)

DECODERS={
    (WAVE_FORMAT_PCM, 1, 8, MONO): PCM_INT8_MONO_DECODER,
    (WAVE_FORMAT_PCM, 2, 8, STEREO): PCM_INT8_STEREO_DECODER,
    (WAVE_FORMAT_PCM, 2, 16, MONO): PCM_INT16_MONO_DECODER,
    (WAVE_FORMAT_PCM, 4, 16, STEREO): PCM_INT16_STEREO_DECODER,
    (WAVE_FORMAT_PCM, 3, 24, MONO): PCM_INT24_MONO_DECODER,
    (WAVE_FORMAT_PCM, 6, 24, STEREO): PCM_INT24_STEREO_DECODER,
    (WAVE_FORMAT_PCM, 4, 32, MONO): PCM_INT32_MONO_DECODER,
    (WAVE_FORMAT_PCM, 8, 32, STEREO): PCM_INT32_STEREO_DECODER,
    (WAVE_FORMAT_IEEE_FLOAT, 4, 32, MONO): IEEE_FLOAT32_MONO_DECODER,
    (WAVE_FORMAT_IEEE_FLOAT, 8, 32, STEREO): IEEE_FLOAT32_STEREO_DECODER,
}

class Reader:
    def __init__(self, path):
        self.stream = open(path, 'rb')
        self.state = SimpleNamespace()
        self.state.format = None
        self.state.nSamplesPerSec = None
        self.state.nChannels = None
        self.state.wBitsPerSample = None
        self.state.nBlockAlign = None

        self.readWaveHeader(self.stream)
        while True:
            ck = self.readNextChunk(self.stream)
            if ck == b'data':
                break
        else:
            raise TypeError("Data chunk not found")

    def close(self):
        self.stream.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    @property
    def srate(self):
        return self.state.nSamplesPerSec

    @property
    def nchannels(self):
        return self.state.nChannels

    def assertTrue(self, test, msg, *args):
        if not test:
            raise TypeError(msg.format(args))

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
        # print(ckID, ckHandler)
        ckHandler(self, stream, ckID, cksize)
        return ckID

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
        self.state.nChannels = chunk16.nChannels
        self.state.nSamplesPerSec = chunk16.nSamplesPerSec
        self.state.nBlockAlign = chunk16.nBlockAlign
        self.state.wBitsPerSample = chunk16.wBitsPerSample


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
        self.decoder = DECODERS[self.state.format, self.state.nBlockAlign, self.state.wBitsPerSample, self.state.nChannels]
        self.nDataSamples = cksize//self.state.nBlockAlign

    def read(self, count):
        """ Read count samples from the data chunk
        """
        nChannels = self.state.nChannels
        maxBufferSize = 4*self.state.nBlockAlign

        count = min(count, self.nDataSamples)
        if not count:
            return None

        buffer = self.stream.read(count*self.state.nBlockAlign)

        self.nDataSamples -= count

        return self.decoder(buffer)

    chunkHandlers = {
        b'fmt ': handlefmt_Chunk,
        b'data': handledataChunk,
    }

def clip(mn, v, mx):
    if v < mn:
        return mn
    if v > mx:
        return mx
    return v

def IEEE_FLOAT32_ENCODER(stream, samples):
    _int = int
    _clip = clip

    for data in itertools.chain(*zip(*samples)):
        stream.write(_IEEE_FLOAT32.pack(data))

def PCM_INT8_ENCODER(stream, samples):
    _int = int
    _clip = clip
    stream.write(bytes([
        clip(0,_int(sample*128.0+128.0),255) for sample in itertools.chain(*zip(*samples))
    ]))

def PCM_SIGNED_INT_ENCODER(stream, samples, bytesperchannel):
    _int = int
    _itb = int.to_bytes
    _clip = clip
    amp = float(1<<8*bytesperchannel-1)
    mn = int(-amp)
    mx = int(amp-1)

    for data in [ _itb(_clip(mn,_int(sample*amp),mx), bytesperchannel, 'little', signed=True) for sample in itertools.chain(*zip(*samples))]:
        stream.write(data)

def PCM_INT16_ENCODER(stream, samples):
    return PCM_SIGNED_INT_ENCODER(stream, samples, 2)

def PCM_INT24_ENCODER(stream, samples):
    return PCM_SIGNED_INT_ENCODER(stream, samples, 3)

def PCM_INT32_ENCODER(stream, samples):
    return PCM_SIGNED_INT_ENCODER(stream, samples, 4)

class Writer:
    """ A class to write Wav files
    """
    def __init__(self, nSamplesPerSec, wBitsPerSample, nChannels, path, *, format=None):
        self.stream = open(path, 'wb')

        if format is None:
            format = WAVE_FORMAT_IEEE_FLOAT

        self.cleanup = []
        self.state = SimpleNamespace()
        self.state.format = format
        self.state.nChannels = nChannels
        self.state.nSamplesPerSec = nSamplesPerSec
        self.state.nAvgBytesPerSec = nSamplesPerSec*nChannels*wBitsPerSample//8
        self.state.nBlockAlign = nChannels*wBitsPerSample//8
        self.state.wBitsPerSample = wBitsPerSample


        self.encoder, *chunks = ENCODERS[format, wBitsPerSample]

        for chunk in chunks:
            chunk(self)

    def close(self):
        self.filelength = self.stream.tell()
        for pos, f in self.cleanup:
            self.stream.seek(pos)
            self.stream.write(f(self).to_bytes(4, 'little'))
        self.stream.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def write(self, samples):
        assert len(samples) == self.state.nChannels

        self.encoder(self.stream, samples)
        self.data_end = self.stream.tell()

    def write_header(self):
        self.stream.write(b'RIFF')

        self.cleanup.append(
            (self.stream.tell(), lambda self: self.filelength-4)
        )
        self.stream.write(b'\x00\x00\x00\x00')
        self.stream.write(b'WAVE')

    def write_fmt16(self):
        self.stream.write(b'fmt ')

        self.cleanup.append((self.stream.tell(), lambda self : self.fmt_end-self.fmt_start))
        self.stream.write(b'\x00\x00\x00\x00')
        self.fmt_start = self.stream.tell()

        ck = PARSER[b'fmt 16'].pack(self.state.format,
                                   self.state.nChannels,
                                   self.state.nSamplesPerSec,
                                   self.state.nAvgBytesPerSec,
                                   self.state.nBlockAlign,
                                   self.state.wBitsPerSample)
        self.stream.write(ck)
        self.fmt_end = self.stream.tell()

    def write_fmt40(self):
        self.state.subformat = self.state.format
        self.state.format = WAVE_FORMAT_EXTENSIBLE

        self.write_fmt16()

        ck = PARSER[b'fmt 18'].pack(22)
        self.stream.write(ck)

        ck = PARSER[b'fmt 40'].pack(self.state.wBitsPerSample,
                                    0,
                                    self.state.subformat,
                                    b'\x00\x00\x00\x00\x10\x00\x80\x00\x00\xAA\x00\x38\x9B\x71')
        self.stream.write(ck)
        self.fmt_end = self.stream.tell()

    def write_fact(self):
        self.stream.write(b'fact')
        self.stream.write((4).to_bytes(4, 'little'))

        self.cleanup.append((self.stream.tell(), lambda self : (self.data_end-self.data_start)//(self.state.nChannels*self.state.nBlockAlign)))
        self.stream.write(b'\x00\x00\x00\x00')

    def write_data(self):
        self.stream.write(b'data')

        self.cleanup.append((self.stream.tell(), lambda self : (self.data_end-self.data_start)))
        self.stream.write(b'\x00\x00\x00\x00')

        self.data_start = self.data_end = self.stream.tell()

ENCODERS ={
    (WAVE_FORMAT_PCM, 8): (PCM_INT8_ENCODER, Writer.write_header, Writer.write_fmt16, Writer.write_data),
    (WAVE_FORMAT_PCM, 16): (PCM_INT16_ENCODER, Writer.write_header, Writer.write_fmt16, Writer.write_data),
    (WAVE_FORMAT_PCM, 24): (PCM_INT24_ENCODER, Writer.write_header, Writer.write_fmt40, Writer.write_fact, Writer.write_data),
    (WAVE_FORMAT_PCM, 32): (PCM_INT32_ENCODER, Writer.write_header, Writer.write_fmt40, Writer.write_fact, Writer.write_data),
    (WAVE_FORMAT_IEEE_FLOAT, 32): (IEEE_FLOAT32_ENCODER, Writer.write_header, Writer.write_fmt40, Writer.write_fact, Writer.write_data),
}

