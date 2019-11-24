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

    def test_2(self):
        """ Generators should share their context with the next generation
        """
        K=123.456
        N=10
        g = constant(CONTEXT, K)

        for i in range(10):
            self.assertEqual(g.context.srate, SRATE)

            samples, g = g(N)

    def test_3(self):
        """ The ramp generator should produce values in the [min,max] range
        """

        N=10
        g = ramp(Context(srate=3))
        samples, g = g(N)

        self.assertEqual(samples, sample(-1,0,+1))

        for i in range(10):
            samples, g = g(N)
            self.assertEqual(samples, sample())

    def test_4(self):
        """ The _call_ generator should produce data from an external source
        """
        x = 0
        def f():
            nonlocal x
            x += 1
            return x

        src = call(f)
        result = []
        for n in range(1,5):
            data, src = src(n)
            result.extend(data)

        self.assertEqual(result, [float(v) for v in range(1,11)])
