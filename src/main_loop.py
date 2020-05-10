import select

from request import Request

resp = b"""HTTP/1.0 200 OK
Date: Mon, 1 Jan 1996 01:01:01 GMT
Content-Type: text/plain
Content-Length: 4

xx
""".replace(b'\n', b'\r\n')


class MainLoop(object):
    READ_SIZE = 4096

    def __init__(self, serversock):
        self._epoll = None
        self._serversock = serversock
        self._connections = {}
        self._requests = {}

    def run(self):
        self._epoll = select.epoll()
        self._epoll.register(self._serversock, select.EPOLLIN)

        # TODO - try/except
        while True:
            for fileno, event in self._epoll.poll(1):
                self._process_socket_event(fileno, event)

    def _process_socket_event(self, fileno, event):
        print(fileno, event)
        if not self._epoll:
            raise RuntimeError('epoll is not initialized')

        if fileno == self._serversock.fileno() and event == select.EPOLLIN:
            # new connection
            conn, addr = self._serversock.accept()
            conn.setblocking(False)
            self._connections[conn.fileno()] = conn
            self._requests[conn.fileno()] = Request()
            # subscribe for connection new data event
            self._epoll.register(conn, select.EPOLLIN)

        elif event == select.EPOLLIN:
            # client socket is ready for reading
            data = self._connections[fileno].recv(self.READ_SIZE)
            self._requests[fileno].extend(data)
            if not data or self._requests[fileno].is_full():
                # ready to send response, switch subscription
                self._epoll.modify(fileno, select.EPOLLOUT)

        elif event == select.EPOLLOUT:
            print('send response')
            bytes_sent = self._connections[fileno].send(resp)
            print('sent', bytes_sent)
            # TODO accumulate and compare with total
            if not bytes_sent or bytes_sent == len(resp):
                print('close connection')
                self._close_connection(fileno)
        else:
            print('close connection')
            self._close_connection(fileno)

    def _close_connection(self, fileno):
        # client disconnected
        self._connections[fileno].close()
        del self._connections[fileno]
