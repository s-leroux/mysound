import unittest

from mysound.context import Context
from mysound.generator import ramp, sample, constant
from mysound.processor import loop, pick
from mysound.time import seconds

import random

class ProcessorTest(unittest.TestCase):
    def test_1(self):
        """ The loop processor should repeat the same signal
        """
        ctx = Context(srate=3)
        r = ramp(ctx, seconds(1))
        l = loop(r)

        for i in range(20):
            samples, l = l(random.randint(3,10))

            self.assertEqual(samples, sample(-1,0,1))

    def test_2(self):
        """ The pick processor must pick n samples from the first signal
            then switch to the second
        """
        ctx = Context(srate=44100)
        s1 = constant(ctx, 1.0)
        s2 = constant(ctx, 0.5)

        p = pick(ctx, 5, s1, s2)
        result = []

        while len(result) < 15:
            data, p = p(min(3, 15-len(result)))
            result.extend(data)

        self.assertEqual(result, [1.0]*5 + [0.5]*10)

