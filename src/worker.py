import socket
import select

BACKLOG = 100

serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

serversock.bind(('', 8080))

serversock.listen(BACKLOG)
serversock.setblocking(False)

epoll = select.epoll()
epoll.register(serversock, select.EPOLLIN)

connections = {}
requests = {}

while True:
    for fileno, event in epoll.poll(1):
        print(fileno, event)
        if fileno == serversock.fileno():
            # new connection
            conn, addr = serversock.accept()
            conn.setblocking(False)
            connections[conn.fileno()] = conn
            requests[conn.fileno()] = bytearray()
            epoll.register(conn, select.EPOLLIN)
        elif event & select.EPOLLIN:
            # client socket is ready for reading
            data = connections[fileno].recv(1024)
            if not data:
                # client disconnected
                connections[fileno].close()
                del connections[fileno]
            else:
                requests[fileno] += data

        print(requests)
