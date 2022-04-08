from socket import *
from select import select
from time import time
from datetime import datetime


SERVER_PORT = 8080
TIMEOUT = 1


client_socket = socket(AF_INET, SOCK_DGRAM)
client_socket.connect(('', SERVER_PORT))
client_socket.settimeout(TIMEOUT)
client_socket.setblocking(False)

for i in range(1, 11):
    msg = f'Test message number {i}'
    start = time()
    client_socket.send(msg.encode())
    ready = select([client_socket], [], [], TIMEOUT)
    if ready[0]:
        msg = client_socket.recv(1024).decode()
        RTT = time() - start
        print(msg)
        print(f'RTT {RTT}')
        print(f'Ping {i} {datetime.fromtimestamp(start)}')
    else:
        print('Request timed out')
    print('===========================')
