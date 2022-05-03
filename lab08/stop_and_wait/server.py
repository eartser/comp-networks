import argparse

import stopwait
from util import read_file, write_file

CLIENT_FILEPATH = 'data/recv_client_data.txt'
SERVER_FILEPATH = 'data/send_server_data.txt'

parser = argparse.ArgumentParser()
parser.add_argument('host', type=str)
parser.add_argument('port', type=int)
parser.add_argument('timeout', type=int)
parser.add_argument('data_size', type=int)
args = parser.parse_args()

input('Tab Enter to start receiving')
received_client_data = stopwait.recv(args.data_size, args.host, args.port, args.timeout)
write_file(CLIENT_FILEPATH, received_client_data)
print(f'All client data received: {len(received_client_data)} bytes.')
print()
input('Tab Enter to start sending')
server_data = read_file(SERVER_FILEPATH)
stopwait.send(server_data, args.host, args.port, args.timeout)
print('All server data sent.')
