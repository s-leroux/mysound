import unittest

from random import randint, uniform

from mysound.generator import rawdata, call
from mysound.processor import take

from mysound.actions import *

class TestActions(unittest.TestCase):
    def test_1(self):
        """ `loop` should loop over data when the stream is exhausted
        """
        data = list(range(10))

        src = loop(rawdata(data))


        result = []
        while len(result) < 100:
            l = min(randint(1,5), 100-len(result))
            chunk, src = src(l)
            result.extend(chunk)

        self.assertEqual(result, data*10)

    def test_2(self):
        """ `pick` must pick n samples from the first signal
            then switch to the second
        """
        s1 = rawdata([1.0]*100)
        s2 = rawdata([0.5]*100)

        p = pick(5, s1, s2)
        result = []

        while len(result) < 15:
            data, p = p(min(3, 15-len(result)))
            result.extend(data)

        self.assertEqual(result, [1.0]*5 + [0.5]*10)

    def test_3(self):
        """ Caching should ensure repeatability
        """
        src = caching(call(lambda : uniform(-1.0,1.0)))

        d11, cont = take(10, src)
        d12, cont = take(90, cont)

        d21, cont = take(90, src)
        d22, cont = take(10, cont)

        self.assertSequenceEqual(d11+d12, d21+d22)

