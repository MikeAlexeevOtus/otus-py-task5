import select
import time


class Writer(object):
    def __init__(self, epoll, socket, response_buffer):
        self._epoll = epoll
        self._socket = socket
        self._response_buffer = response_buffer
        self._total_sent = 0
        self._last_sent = None
        self._buffer = bytearray()

    def write(self):
        print('writing', id(self), time.time())
        self._buffer += self._response_buffer.get_next_chunk()

        self._last_sent = self._socket.send(self._buffer)
        self._buffer = self._buffer[self._last_sent:]
        self._total_sent += self._last_sent
        self._epoll.register(self._socket, select.EPOLLIN)

    def has_unsent_data(self):
        return len(self._buffer) or self._response_buffer.has_unsent_data()
