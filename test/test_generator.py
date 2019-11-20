import unittest

from pprint import pprint

from mysound.generator import *
from mysound.context import Context

SRATE=44100
CONTEXT = Context(srate=SRATE)

class TestGenerator(unittest.TestCase):
    def test_0(self):
        """ The `sample` function should return an array or length 1
        """
        K=123.456
        s = sample(K)

        self.assertIsInstance(s, array)
        self.assertEqual(len(s), 1)
        self.assertAlmostEqual(s[0], 123.456, places=4)

    def test_1(self):
        """ Constant generator should return a stream of constant values
        """
        K=123.456
        N=10
        g = constant(CONTEXT, K)

        for i in range(10):
            samples, g = g(N)

            self.assertTrue(0 < len(samples) <= N)
            self.assertSequenceEqual(samples,sample(K)*N)

    def test_1(self):
        """ Generators should share their context with the next generation
        """
        K=123.456
        N=10
        g = constant(CONTEXT, K)

        for i in range(10):
            self.assertEqual(g.context.srate, SRATE)

            samples, g = g(N)
