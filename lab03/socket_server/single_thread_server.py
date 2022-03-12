from socket import *
from os.path import exists
from sys import getsizeof


SERVER_HOST = '127.0.0.1'
SERVER_PORT = 2000


def parse_http_request(request):
    body = request.split(sep='\r\n\r\n')[-1]
    return body


def http_ok_response(text):
    return f'''HTTP/1.1 200 OK\r
Content-Length: {getsizeof(text)}\r
Content-Type: "text/plain"\r
\r
{text}'''


def http_error_response():
    msg = '404 Not Found'

    return f'''HTTP/1.1 404 Not Found\r
Content-Length: {getsizeof(msg)}\r
Content-Type: "text/plain"\r
\r
{msg}'''


server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(1)
print('The server is ready to receive.')

while True:
    connection_socket, address = server_socket.accept()
    print(f'New socket for {address}.')

    filename = parse_http_request(connection_socket.recv(1024).decode())
    print(filename)
    if exists(filename):
        print('200 OK')
        f = open(filename)
        connection_socket.send(http_ok_response(f.read()).encode())
        f.close()
    else:
        print('404 Not Found')
        connection_socket.send(http_error_response().encode())

    connection_socket.close()
    print('Socket closed.')
