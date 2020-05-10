class Request(object):
    def __init__(self):
        self._buffer = bytearray()

    def extend(self, chunk):
        self._buffer += chunk

    def __repr__(self):
        return '<Request {}, buffer content: {}>'.format(id(self), self._buffer)
