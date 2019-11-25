import unittest

from mysound.fileformats.dummy import Reader

class TestDummyFileReader(unittest.TestCase):
    def test_1(self):
        data = (
          tuple(range(-10, 10)),
          tuple(range(-5, 15)),
        )
        with Reader(data) as r:
            while True:
                data = r.read(4)
                if not data:
                    break
                # print(data)
