from socket import *
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('server_host', type=str)
parser.add_argument('server_port', type=int)
parser.add_argument('text', type=str, nargs='+')
args = parser.parse_args()

SERVER_HOST = args.server_host
SERVER_PORT = args.server_port
TEXT = ' '.join(args.text)

client_socket = socket(AF_INET6, SOCK_DGRAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))

client_socket.send(TEXT.encode())
recv_text = client_socket.recv(1024).decode()
print(recv_text)
client_socket.close()
