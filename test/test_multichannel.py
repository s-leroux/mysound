import unittest

from mysound.context import Context
from mysound.multichannel import *
from mysound.generator import constant
from mysound.processor import pick

class TestTrack(unittest.TestCase):
    def test_1(self):
        """ We can mux several independent channels to
            produce a multichannel source
        """
        ctx = Context(srate=44100)
        ch1 = constant(ctx, 0.5)
        ch2 = constant(ctx, 1.0)
        ch3 = constant(ctx, 2.0)
        t = mux(
            ch1,
            pick(ctx, 20, ch2, ch3),
            pick(ctx, 13, ch2, ch3),
        )

        r0 = []
        r1 = []
        r2 = []
        while len(r0) < 30:
            data, t = t(min(9, 30-len(r0)))
            r0.extend(data[0])
            r1.extend(data[1])
            r2.extend(data[2])
        
        self.assertEqual(r0, [0.5]*30)
        self.assertEqual(r1, [1.0]*20 + [2.0]*10)
        self.assertEqual(r2, [1.0]*13 + [2.0]*17)

    def test_2(self):
        """ The demuxer should produce an array of
            independent channels from a multichannel source
        """
        data = (
          tuple(range(-10, 10)),
          tuple(range(-5, 15)),
        )

        src = rawdata(*data)
        channels = demux(2, src)
        for j in range(2):
            ch1, ch2 = channels
            d1 = []
            d2 = []
            while True:
                v, ch1 = ch1(3)
                # print(v)
                if not v:
                    break

                d1.extend(v)
            while True:
                v, ch2 = ch2(3)
                # print(v)
                if not v:
                    break

                d2.extend(v)

            self.assertSequenceEqual(d1, data[0])
            self.assertSequenceEqual(d2, data[1])


