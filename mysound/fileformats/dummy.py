""" Dummy file format for testing purpose.
"""

from array import array

class Reader:
    def __init__(self, data):
        self.data = data
        self.offset = 0

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    @property
    def srate(self):
        return 44100

    @property
    def nchannels(self):
        return len(self.data)

    def read(self, count):
        count = 4

        start = self.offset
        stop = self.offset = start+count
        if start >= len(self.data[0]):
            return None

        return [array('f', d[start:stop]) for d in self.data]
