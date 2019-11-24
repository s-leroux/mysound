import unittest

from mysound.fileformats import *
from mysound.fileformats.dummy import Reader

class TestUtilities(unittest.TestCase):
    def setUp(self):
        self.data = (
          tuple(range(-10, 10)),
          tuple(range(-5, 15)),
        )

        self.file = Reader(self.data)

    def tearDown(self):
        self.file.close()

    def test_1(self):
        first = blockReader(self.file)

        for i in range(4):
            reader = first
            d1 = []
            d2 = []
            for j in range(6):
                v1, c1 = reader()
                v2, c2 = reader()

                if v1:
                    d1.extend(v1[0])
                    d2.extend(v2[1])
                    self.assertEqual(len(v1), 2)
                    self.assertEqual(len(v1[0]), 4)
                    self.assertEqual(v1, v2)
                # print(i,j,v1)
                reader = c1
            self.assertSequenceEqual(d1, self.data[0])
            self.assertSequenceEqual(d2, self.data[1])

