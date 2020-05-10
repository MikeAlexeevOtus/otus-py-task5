resp = b"""HTTP/1.0 200 OK
Date: Mon, 1 Jan 1996 01:01:01 GMT
Content-Type: text/plain
Content-Length: 4

xx
""".replace(b'\n', b'\r\n')


class Writer(object):
    def __init__(self, socket):
        self._socket = socket
        self._total_sent = 0
        self._last_sent = None
        self._enabled = False

    def write(self):
        if not self._enabled:
            raise RuntimeError('writer is disabled, can not write')

        self._last_sent = self._socket.send(resp)
        self._total_sent += self._last_sent

    def is_write_completed(self):
        if self._last_sent is None:
            return False

        return not self._last_sent or self._total_sent == len(resp)

    def enable(self):
        self._enabled = True
