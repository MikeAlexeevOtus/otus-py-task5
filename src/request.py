class Request(object):
    EOF1 = b'\n\n'
    EOF2 = b'\n\r\n'

    def __init__(self):
        self._buffer = bytearray()

    def extend(self, chunk):
        self._buffer += chunk

    def is_full(self):
        return self.EOF1 in self._buffer or self.EOF2 in self._buffer

    def __repr__(self):
        return '<Request {}, buffer content: {}>'.format(id(self), self._buffer)
