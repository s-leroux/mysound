import unittest

from mysound.context import Context
from mysound.time import *

SRATE = (
    44100,
    8000,
)

CONTEXT = (
  Context(srate=SRATE[0]),
  Context(srate=SRATE[1]),
)

class TestTime(unittest.TestCase):
    def test_1(self):
        """ Sample unit are contant regardless of the sampling rate
        """
        duration = samples(1000)
        s = [duration(ctx) for ctx in CONTEXT]

        self.assertEqual(*s)

    def test_2(self):
        """ Integer seconds are converted to samples according to the sampling rate
        """
        D=3
        duration = seconds(int(D))
        s = [duration(ctx) for ctx in CONTEXT]

        for srate, samples in zip(SRATE, s):
            self.assertEqual(samples, D*srate)

    def test_3(self):
        """ Fractional seconds are converted to samples according to the sampling rate
        """
        D=3.5
        duration = seconds(D)
        s = [duration(ctx) for ctx in CONTEXT]

        for srate, samples in zip(SRATE, s):
            self.assertEqual(samples, D*srate)

    def test_4(self):
        """ hms duration are converted to samples according to the sampling rate
        """
        H=1
        M=2
        S=3
        duration = hms(H,M,S)
        s = [duration(ctx) for ctx in CONTEXT]

        for srate, samples in zip(SRATE, s):
            self.assertEqual(samples, (H*3600+M*60+S)*srate)


class TestTimeConversion(unittest.TestCase):
    def test_1(self):
        """ `to_samples` should pass integers unchanged regardless of the context
        """
        duration = int(123)

        self.assertEqual(to_samples(CONTEXT[0], duration), duration)
        self.assertEqual(to_samples(CONTEXT[1], duration), duration)

    def test_2(self):
        """ `to_samples` should convert from seconds according to the context
        """
        D = 3.5
        duration = seconds(D)

        for srate, ctx in zip(SRATE, CONTEXT):
            self.assertEqual(to_samples(ctx, duration), D*srate)

    def test_2(self):
        """ `to_samples` should convert from hms according to the context
        """
        H=1
        M=2
        S=3
        duration = hms(H,M,S)

        for srate, ctx in zip(SRATE, CONTEXT):
            self.assertEqual(to_samples(ctx, duration), (H*3600+M*60+S)*srate)
