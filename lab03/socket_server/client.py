from socket import *
from sys import getsizeof
import argparse


def http_request(text):
    return f'''GET / HTTP/1.1\r
Content-Length: {getsizeof(text)}\r
Content-Type: "text/plain"\r
\r
{text}'''


def parse_http_response(request):
    body = request.split(sep='\r\n\r\n')[-1]
    return body


parser = argparse.ArgumentParser()
parser.add_argument('server_host', type=str)
parser.add_argument('server_port', type=int)
parser.add_argument('filename', type=str)
args = parser.parse_args()

SERVER_HOST = args.server_host
SERVER_PORT = args.server_port
FILENAME = args.filename

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))

client_socket.send(http_request(FILENAME).encode())
text = parse_http_response(client_socket.recv(1024).decode())
print(text)
client_socket.close()
