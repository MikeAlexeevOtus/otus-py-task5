import select
import queue
import threading
import logging

from response import Response
from request import Request


def writers_thread_run(queue, writers):
    while True:
        try:
            fd = queue.get()
            logging.debug('getting next queue item for processing')
            writer = writers[fd]
            writer.write()
        except Exception:
            logging.exception('error in writers thread')


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

    def has_unread_data(self):
        if self._last_recieved is None:
            # have not read any yet
            return True
        elif self.request.is_full() or not self._last_recieved:
            # we have read enough
            return False
        return True


class Writer(object):
    def __init__(self, epoll, socket, response_buffer):
        self._epoll = epoll
        self._socket = socket
        self._response_buffer = response_buffer
        self._buffer = bytearray()

    def write(self):
        if not self._buffer:
            self._buffer += self._response_buffer.get_next_chunk()

        logging.debug('sending %s', str(self._buffer))
        sent = self._socket.send(self._buffer)
        logging.debug('sent %d bytes', sent)
        self._buffer = self._buffer[sent:]

        # we are ready to send again
        self._epoll.register(self._socket, select.EPOLLOUT)

    def has_unsent_data(self):
        return len(self._buffer) or self._response_buffer.has_unsent_data()


class MainLoop(object):
    def __init__(self, serversock, docs_root):
        self._docs_root = docs_root
        self._serversock = serversock
        self._epoll = None
        self._connections = {}
        self._readers = {}
        self._writers = {}
        self._writers_queue = queue.Queue()
        self._writers_thread = threading.Thread(target=writers_thread_run,
                                                args=(self._writers_queue, self._writers,),
                                                daemon=True)

    def run(self):
        self._epoll = select.epoll()
        self._epoll.register(self._serversock, select.EPOLLIN)
        self._writers_thread.start()

        while True:
            try:
                for fileno, event in self._epoll.poll(1):
                    self._process_epoll_event(fileno, event)
            except Exception:
                logging.exception('error in main thread')

    def _process_epoll_event(self, fileno, event):
        logging.debug('processing epoll event, fd: %d, event: %d', fileno, event)
        if not self._epoll:
            raise RuntimeError('epoll is not initialized')

        if fileno == self._serversock.fileno() and event == select.EPOLLIN:
            # new connection
            conn, addr = self._serversock.accept()
            conn.setblocking(False)
            request = Request()
            resp_buffer = Response(request, self._docs_root)

            self._connections[conn.fileno()] = conn
            self._readers[conn.fileno()] = Reader(conn, request)
            self._writers[conn.fileno()] = Writer(self._epoll, conn, resp_buffer)

            # subscribe for connection new data event
            self._epoll.register(conn, select.EPOLLIN)

        elif event == select.EPOLLIN:
            logging.debug('read request')
            reader = self._readers[fileno]
            reader.read()
            if not reader.has_unread_data():
                # ready to send response, switch epoll subscription
                self._epoll.modify(fileno, select.EPOLLOUT)

        elif event == select.EPOLLOUT:
            logging.debug('send response')
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
        logging.debug('close connection')
        self._epoll.unregister(fileno)
        self._connections[fileno].close()
        del self._connections[fileno]
        del self._readers[fileno]
        del self._writers[fileno]
