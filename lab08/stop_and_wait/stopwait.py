import socket
from random import uniform

from util import *


def send(data, host, port, timeout):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(timeout)

    index = 1

    for i, packet in enumerate(split_data(data)):
        index = (index + 1) % 2
        packet = build_packet(packet, index)

        while True:
            sock.sendto(packet, (host, port))
            print(f'> {i} packet (index={index}) sent.')

            try:
                ack, _ = sock.recvfrom(4)
                if uniform(0, 1) < 0.3:
                    raise socket.timeout()
                if ack == build_ack(index):
                    print(f'+ ACK (index={index}) received.')
                    break

            except socket.timeout:
                print('- Timeout, trying again.')
                continue


def recv(data_size, host, port, timeout):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(timeout)
    sock.bind((host, port))

    expected_index = 0
    received_data = []

    while data_size > 0:
        try:
            packet, address = sock.recvfrom(BATCH_SIZE)
            cur_index, cur_data = parse_packet(packet)
            if uniform(0, 1) < 0.3:
                raise socket.timeout()
            if cur_index == expected_index:
                expected_index = (cur_index + 1) % 2
                received_data.append(cur_data)
                data_size -= len(cur_data)
                print(f'+ {len(received_data) - 1} packet (index={cur_index}) received: {len(cur_data)} bytes.')

            sock.sendto(build_ack(cur_index), address)
            print(f'> ACK (index={cur_index}) sent.')

        except socket.timeout:
            print('- Timeout, trying again.')
            continue

    return ''.join(received_data)
