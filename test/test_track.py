import unittest

from mysound.context import Context
from mysound.track import *
from mysound.generator import constant
from mysound.processor import pick

class TestTrack(unittest.TestCase):
    def test_1(self):
        ctx = Context(srate=44100)
        ch1 = constant(ctx, 0.5)
        ch2 = constant(ctx, 1.0)
        ch3 = constant(ctx, 2.0)
        t = tracks(
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




