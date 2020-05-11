resp = b"""HTTP/1.0 200 OK
Date: Mon, 1 Jan 1996 01:01:01 GMT
Content-Type: text/plain
Content-Length: 4

xx
""".replace(b'\n', b'\r\n')


class ResponseBuffer(object):
    RETURN_CHUNK_SIZE = 4096

    def __init__(self, request, document_root):
        self._request = request
        self._root = document_root
        self._buffer = resp
        self._total_returned = 0

    def get_next_chunk(self):
        chunk = self._buffer[:self.RETURN_CHUNK_SIZE]
        self._total_returned += len(chunk)
        self._buffer = self._buffer[self.RETURN_CHUNK_SIZE:]
        return chunk

    def has_unsent_data(self):
        return len(self._buffer)
