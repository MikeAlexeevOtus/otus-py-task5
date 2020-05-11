import select
import queue
import threading
import time

from reader import Reader
from writer import Writer
from response_buffer import ResponseBuffer
from request import Request


def writers_thread_run(queue, writers):
    while True:
        fd = queue.get()
        print('next queue item')
        writer = writers[fd]
        writer.write()


class MainLoop(object):
    def __init__(self, serversock):
        self._epoll = None
        self._serversock = serversock
        self._connections = {}
        self._readers = {}
        self._writers = {}
        self._writers_queue = queue.Queue()
        self._writers_thread = threading.Thread(target=writers_thread_run,
                                                args=(self._writers_queue, self._writers))

    def run(self):
        self._epoll = select.epoll()
        self._epoll.register(self._serversock, select.EPOLLIN)
        self._writers_thread.start()

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
            request = Request()
            resp_buffer = ResponseBuffer(request, '/tmp/share')

            self._connections[conn.fileno()] = conn
            self._readers[conn.fileno()] = Reader(conn, request)
            self._writers[conn.fileno()] = Writer(self._epoll, conn, resp_buffer)

            # subscribe for connection new data event
            self._epoll.register(conn, select.EPOLLIN)

        elif event == select.EPOLLIN:
            print('read request')
            reader = self._readers[fileno]
            reader.read()
            if reader.is_read_completed():
                # ready to send response, switch epoll subscription
                self._epoll.modify(fileno, select.EPOLLOUT)

        elif event == select.EPOLLOUT:
            print('send response', time.time())
            writer = self._writers[fileno]
            if not writer.has_unsent_data():
                self._close_connection(fileno)
                return

            # prevent tasks dups
            self._epoll.unregister(fileno)
            self._writers_queue.put(fileno)

        else:
            self._close_connection(fileno)

    def _close_connection(self, fileno):
        print('close connection', time.time())
        self._epoll.unregister(fileno)
        self._connections[fileno].close()
        del self._connections[fileno]
        del self._readers[fileno]
        del self._writers[fileno]
