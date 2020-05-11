class Reader(object):
    READ_SIZE = 4096

    def __init__(self, socket, request):
        self._socket = socket
        self.request = request
        self._last_recieved = None

    def read(self):
        data = self._socket.recv(self.READ_SIZE)
        self._last_recieved = len(data)
        self.request.extend(data)

    def is_read_completed(self):
        if self._last_recieved is None:
            return False

        return not self._last_recieved or self.request.is_full()
