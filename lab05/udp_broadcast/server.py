from socket import *
from datetime import datetime
from time import sleep


server_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
server_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

while True:
    msg = datetime.now().strftime("%H:%M:%S").encode()
    server_socket.sendto(msg, ('<broadcast>', 37020))
    sleep(1)
