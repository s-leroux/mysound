import unittest

import os.path

from mysound.fileformats.wave import Reader, Writer, WAVE_FORMAT_PCM, WAVE_FORMAT_IEEE_FLOAT

WAVEFILES = [os.path.join('.', 'test', 'data', fname) for fname in (
    'ieee_float32_1.wav',
    'ieee_float32_2.wav',
    'pcm_int16_1.wav',
    'pcm_int16_2.wav',
    'pcm_int24_1.wav',
    'pcm_int24_2.wav',
    'pcm_int32_1.wav',
    'pcm_int32_2.wav',
    'pcm_int8_1.wav',
    'pcm_int8_2.wav',
)]

TMP_FILE = os.path.join('.', 'test', 'tmp', '{}_{}_{}.wav')

class TestWaveReader(unittest.TestCase):
    def test_1(self):
        """ WaveReader can read valid wave files
        """
        for f in WAVEFILES:
            with Reader(f) as wav:
                while True:
                    chunk = wav.read(256)
                    if not chunk:
                        break


class TestWaveWriter(unittest.TestCase):
    def test_1(self):
        """ WaveReader can read valid wave files
        """
        samples = [ [-1.0]*40200 + [0.0]*80400 + [1.0]*40200 ]
        for nChannels in (1,2):
            for nBits in (8, 16, 24, 32):
                fname = TMP_FILE.format('pcm', nBits, nChannels)
                with Writer(48000, nBits, nChannels, fname, format=WAVE_FORMAT_PCM) as wav:
                    wav.write(samples*nChannels)
        for nChannels in (1,2):
            for nBits in (32,):
                fname = TMP_FILE.format('float', nBits, nChannels)
                with Writer(48000, nBits, nChannels, fname, format=WAVE_FORMAT_IEEE_FLOAT) as wav:
                    wav.write(samples*nChannels)
