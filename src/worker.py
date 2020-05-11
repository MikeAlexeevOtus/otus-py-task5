import socket
import argparse
import pathlib

from main_loop import MainLoop


def init_serversocket(addr, port, backlog):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((addr, port))
    sock.listen(backlog)
    sock.setblocking(False)

    return sock


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--docs-root', '-r', type=pathlib.Path, required=True)
args = arg_parser.parse_args()

serversock = init_serversocket('', 8080, 100)
loop = MainLoop(serversock, args.docs_root)
loop.run()
