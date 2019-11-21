import unittest

import os.path

from mysound.fileformats.wave import WaveReader

WAVEFILES = [os.path.join('.', 'test', 'data', fname) for fname in (
    'pcm_float32_1.wav',
    'pcm_float32_2.wav',
    'pcm_int16_1.wav',
    'pcm_int16_2.wav',
    'pcm_int24_1.wav',
    'pcm_int24_2.wav',
    'pcm_int32_1.wav',
    'pcm_int32_2.wav',
    'pcm_int8_1.wav',
    'pcm_int8_2.wav',
)]

class TestWaveReader(unittest.TestCase):
    def test_1(self):
        """ WaveReader can read valid wave files
        """
        for f in WAVEFILES:
            for chunk in WaveReader.fromFile(f):
                pass
            print(chunk)
