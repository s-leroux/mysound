import unittest

import os.path

from mysound.fileformats.wave import WaveReader, WaveWriter, WAVE_FORMAT_PCM, WAVE_FORMAT_IEEE_FLOAT

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
            for chunk in WaveReader.fromFile(f):
                pass
            print(chunk)

class TestWaveWriter(unittest.TestCase):
    def test_1(self):
        """ WaveReader can read valid wave files
        """
        samples = [ [0.0]*160800 ]
        for nChannels in (1,2):
            for nBits in (8, 16, 24, 32):
                with open(TMP_FILE.format('pcm', nBits, nChannels), 'wb') as f:
                    wav = WaveWriter(f, WAVE_FORMAT_PCM, 48000, nBits, nChannels)
                    wav.write(samples*nChannels)
                    wav.close()
        for nChannels in (1,2):
            for nBits in (32,):
                with open(TMP_FILE.format('float', nBits, nChannels), 'wb') as f:
                    wav = WaveWriter(f, WAVE_FORMAT_IEEE_FLOAT, 48000, nBits, nChannels)
                    wav.write(samples*nChannels)
                    wav.close()
