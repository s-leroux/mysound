import unittest

from mysound.context import Context
from mysound.generator import ramp, sample
from mysound.processor import loop

import random

class ProcessorTest(unittest.TestCase):
    def test_1(self):
        """ The loop processor should repeat the same signal
        """
        ctx = Context(srate=3)
        r = ramp(ctx, 1)
        l = loop(ctx, r)

        for i in range(20):
            samples, l = l(random.randint(3,10))

            self.assertEqual(samples, sample(-1,0,1))

