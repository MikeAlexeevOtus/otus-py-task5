import socket

from main_loop import MainLoop


def init_serversocket(addr, port, backlog):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((addr, port))
    sock.listen(backlog)
    sock.setblocking(False)

    return sock


serversock = init_serversocket('', 8080, 100)
loop = MainLoop(serversock)
loop.run()
