import unittest

from pprint import pprint

from mysound.context import Context

class TestContext(unittest.TestCase):
    def test_0(self):
        """ The context can hold the sampling rate
        """
        c = Context(srate=44100)

        self.assertEqual(c.srate, 44100)
