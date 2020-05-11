class Request(object):
    EOF1 = b'\n\n'
    EOF2 = b'\r\n\r\n'

    def __init__(self):
        self._buffer = bytearray()

    def extend(self, chunk):
        self._buffer += chunk

    def is_full(self):
        return self.EOF2 in self._buffer or self.EOF1 in self._buffer

    def __repr__(self):
        return '<Request {}, buffer content: {}>'.format(id(self), self._buffer)

    @property
    def url(self):
        if not self.is_full():
            raise RuntimeError('request is not read yet')
        return self._buffer.split(b' ', 2)[1].decode()

    @property
    def verb(self):
        if not self.is_full():
            raise RuntimeError('request is not read yet')
        return self._buffer.split(b' ', 1)[0].decode()
