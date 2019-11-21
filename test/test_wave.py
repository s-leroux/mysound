import unittest

import os.path

from mysound.fileformats.wave import WaveReader

WAVEFILE = os.path.join('.', 'test', 'data', 'ping1000hz.wav')

class TestWaveReader(unittest.TestCase):
    def test_1(self):
        """ WaveReader can read valid wave files
        """
        wav = WaveReader.fromFile(WAVEFILE)
