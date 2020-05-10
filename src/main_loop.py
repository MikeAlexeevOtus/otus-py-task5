import select

from reader import Reader
from writer import Writer


class MainLoop(object):
    def __init__(self, serversock):
        self._epoll = None
        self._serversock = serversock
        self._connections = {}
        self._readers = {}
        self._writers = {}

    def run(self):
        self._epoll = select.epoll()
        self._epoll.register(self._serversock, select.EPOLLIN)

        # TODO - try/except
        while True:
            for fileno, event in self._epoll.poll(1):
                self._process_epoll_event(fileno, event)

    def _process_epoll_event(self, fileno, event):
        print(fileno, event)
        if not self._epoll:
            raise RuntimeError('epoll is not initialized')

        if fileno == self._serversock.fileno() and event == select.EPOLLIN:
            # new connection
            conn, addr = self._serversock.accept()
            conn.setblocking(False)
            self._connections[conn.fileno()] = conn
            self._readers[conn.fileno()] = Reader(conn)
            self._writers[conn.fileno()] = Writer(conn)
            # subscribe for connection new data event
            self._epoll.register(conn, select.EPOLLIN)

        elif event == select.EPOLLIN:
            print('read request')
            self._readers[fileno].read()
            if self._readers[fileno].is_read_completed():
                # ready to send response, switch subscription
                self._epoll.modify(fileno, select.EPOLLOUT)

        elif event == select.EPOLLOUT:
            print('send response')
            self._writers[fileno].write()
            if self._writers[fileno].is_write_completed():
                self._close_connection(fileno)
        else:
            self._close_connection(fileno)

    def _close_connection(self, fileno):
        print('close connection')
        self._epoll.unregister(fileno)
        self._connections[fileno].close()
        del self._connections[fileno]
        del self._readers[fileno]
        del self._writers[fileno]
