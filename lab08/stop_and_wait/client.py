import argparse

import stopwait
from util import read_file, write_file

CLIENT_FILEPATH = 'data/send_client_data.txt'
SERVER_FILEPATH = 'data/recv_server_data.txt'

parser = argparse.ArgumentParser()
parser.add_argument('host', type=str)
parser.add_argument('port', type=int)
parser.add_argument('timeout', type=int)
parser.add_argument('data_size', type=int)
args = parser.parse_args()

input('Tab Enter to start sending')
client_data = read_file(CLIENT_FILEPATH)
stopwait.send(client_data, args.host, args.port, args.timeout)
print('All client data has been sent.')
print()
input('Tab Enter to start receiving')
received_server_data = stopwait.recv(args.data_size, args.host, args.port, args.timeout)
write_file(SERVER_FILEPATH, received_server_data)
print(f'All server data received: {len(received_server_data)} bytes.')
