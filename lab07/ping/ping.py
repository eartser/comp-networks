from socket import *
from select import select
from time import time
import argparse


def avg(arr):
    return sum(arr) / len(arr)


def std(arr):
    return (sum([x ** 2 for x in arr]) / len(arr) - (sum(arr) / len(arr)) ** 2) ** 0.5


parser = argparse.ArgumentParser()
parser.add_argument('SERVER_PORT', type=int)
parser.add_argument('TIMEOUT', type=int)
parser.add_argument('--N', type=int, default=10)

args = parser.parse_args()


SERVER_PORT = args.SERVER_PORT
TIMEOUT = args.TIMEOUT
N = args.N


client_socket = socket(AF_INET, SOCK_DGRAM)
client_socket.connect(('', SERVER_PORT))
client_socket.settimeout(TIMEOUT)
client_socket.setblocking(False)

times = []
common_start = time()

for i in range(1, N + 1):
    msg = f'Test message number {i}'
    start = time()
    client_socket.send(msg.encode())
    ready = select([client_socket], [], [], TIMEOUT)
    if ready[0]:
        msg = client_socket.recv(1024).decode()
        end = time()
        RTT = end - start
        time_passed = end - common_start
        times.append(RTT)
        print(f'{i} packets transmitted, {len(times)} packets received, {round((1 - len(times) / i) * 100)}% packet loss, time {round(time_passed * 1000)}ms')
        print(f'rtt min/avg/max/mdev = {round(min(times) * 1000, 3)}/{round(avg(times) * 1000, 3)}/{round(max(times) * 1000, 3)}/{round(std(times) * 1000, 3)} ms')
        print()
