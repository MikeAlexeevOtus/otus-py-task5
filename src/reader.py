from request import Request


class Reader(object):
    READ_SIZE = 4096

    def __init__(self, socket):
        self._socket = socket
        self._request = Request()
        self._last_recieved = None

    def read(self):
        data = self._socket.recv(self.READ_SIZE)
        self._last_recieved = len(data)
        self._request.extend(data)

    def is_read_completed(self):
        if self._last_recieved is None:
            return False

        return not self._last_recieved or self._request.is_full()
