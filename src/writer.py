class Writer(object):
    def __init__(self, socket):
        self._socket = socket
        self._total_sent = 0
        self._last_sent = None
        self._buffer = bytearray()

    def write(self):
        self._last_sent = self._socket.send(self._buffer)
        self._buffer = self._buffer[self._last_sent:]
        self._total_sent += self._last_sent

    def is_write_completed(self):
        return self._last_sent == 0

    def add_data(self, data):
        self._buffer += data

    def has_unsent_data(self):
        return len(self._buffer)
