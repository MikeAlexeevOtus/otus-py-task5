import socket
from main_loop import MainLoop

BACKLOG = 100

serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

serversock.bind(('', 8080))

serversock.listen(BACKLOG)
serversock.setblocking(False)


loop = MainLoop(serversock)
loop.run()
