import os
import argparse
import pathlib
import socket
import logging

from main_loop import MainLoop

BACKLOG = 10000


def init_serversocket(addr, port, backlog):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.bind((addr, port))
    sock.listen(backlog)
    sock.setblocking(False)

    return sock


worker_pids = []

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--docs-root', '-r', type=pathlib.Path, required=True)
arg_parser.add_argument('--port', '-p', type=int, default=8080)
arg_parser.add_argument('--addr', '-i', type=str, default='127.0.0.1')
arg_parser.add_argument('--workers', '-w', type=int, default=4)
arg_parser.add_argument('--debug', '-d', action='store_true')
args = arg_parser.parse_args()

serversock = init_serversocket(args.addr, args.port, BACKLOG)

logging.basicConfig(
    format='[%(asctime)s] %(process)d:%(threadName)s %(levelname).1s - %(message)s',
    datefmt='%Y.%m.%d %H:%M:%S',
    level=logging.DEBUG if args.debug else logging.INFO
)

logging.info('started master')

for worker in range(args.workers):
    pid = os.fork()
    if pid:
        # in master
        worker_pids.append(pid)
        continue
    else:
        # in worker
        logging.info('started worker')
        loop = MainLoop(serversock, args.docs_root)
        loop.run()

for pid in worker_pids:
    os.waitpid(pid, 0)
