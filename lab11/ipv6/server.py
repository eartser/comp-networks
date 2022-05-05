from socket import *


SERVER_HOST = '::1'
SERVER_PORT = 2000


server_socket = socket(AF_INET6, SOCK_DGRAM)
server_socket.bind((SERVER_HOST, SERVER_PORT))
print('The server is ready to receive.')

while True:
    text, addr = server_socket.recvfrom(1024)
    text = text.decode()
    print(f'Request received: {text}')
    text = text.upper()
    server_socket.sendto(text.encode(), addr)
    print(f'Response sent: {text}')
