from socket import *
from random import uniform


SERVER_PORT = 8080


server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind(('', SERVER_PORT))

while True:
    msg, addr = server_socket.recvfrom(1024)
    if uniform(0, 1) < 0.2:
        continue
    server_socket.sendto(msg.decode().upper().encode(), addr)
