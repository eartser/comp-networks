from socket import *


ip_addr = input('Enter IP-address: ')
min_port, max_port = int(input('Enter min port: ')), int(input('Enter max port: '))

print('List of available ports:')
for port in range(min_port, max_port + 1):
    client_socket = socket(AF_INET, SOCK_STREAM)
    res = client_socket.connect_ex((ip_addr, port))
    if res == 0:
        client_socket.close()
        continue
    print(port)
