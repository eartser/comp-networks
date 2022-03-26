from socket import *


client_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
client_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
client_socket.bind(('', 37020))

while True:
    msg, adr = client_socket.recvfrom(2048)
    print(msg.decode())
