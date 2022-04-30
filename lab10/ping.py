import argparse
import os
import struct
from enum import Enum
from select import select
from socket import *
from time import time, sleep


parser = argparse.ArgumentParser()
parser.add_argument('DESTINATION', type=str)
parser.add_argument('--TIMEOUT', type=int, default=1)
args = parser.parse_args()

ICMP_ECHO_REPLY = 0
ICMP_DESTINATION_UNREACHABLE = 3
ICMP_ECHO_REQUEST = 8

TIMEOUT = args.TIMEOUT


class PingError(Enum):
    OPERATION_TIMEOUT = -1
    NET_UNREACHABLE = 0
    HOST_UNREACHABLE = 1
    PROTOCOL_UNREACHABLE = 2
    PORT_UNREACHABLE = 3
    FRAGMENTATION_NEEDED_AND_DONT_FRAGMENT_WAS_SENT = 4
    SOURCE_ROUTE_FAILED = 5
    DESTINATION_NETWORK_UNKNOWN = 6
    DESTINATION_HOST_UNKNOWN = 7
    SOURCE_HOST_ISOLATED = 8
    COMMUNICATION_WITH_DESTINATION_NETWORK_IS_ADMINISTRATIVELY_PROHIBITED = 9
    COMMUNICATION_WITH_DESTINATION_HOST_IS_ADMINISTRATIVELY_PROHIBITED = 10
    DESTINATION_NETWORK_UNREACHABLE_FOR_TYPE_OF_SERVICE = 11
    DESTINATION_HOST_UNREACHABLE_FOR_TYPE_OF_SERVICE = 12
    COMMUNICATION_ADMINISTRATIVELY_PROHIBITED = 13
    HOST_PRECEDENCE_VIOLATION = 14
    PRECEDENCE_CUTOFF_IN_EFFECT = 15


def checksum(s, reverse=True):
    result = 0
    for i in range(0, len(s), 2):
        b1 = s[i]
        b2 = 0
        if i + 1 < len(s):
            b2 = s[i + 1]
        b = (b2 << 8) + b1
        result += b
    while (result & 0xffff) != result:
        result = (result >> 16) + (result & 0xffff)
    if reverse:
        result = result ^ 0xffff
    return result


def parse_icmp_packet(packet):
    icmp_part = packet[20:]
    icmp_type, icmp_code = struct.unpack('bb', icmp_part[:2])
    if icmp_type == ICMP_ECHO_REPLY and icmp_code == 0:
        icmp_header = icmp_part[:8]
        data = icmp_part[8:]
        icmp_type, icmp_code, checksum, p_id, p_seq = struct.unpack("bbHHh", icmp_header)
        return icmp_type, icmp_code, (checksum, p_id, p_seq, data)
    elif icmp_type == ICMP_DESTINATION_UNREACHABLE:
        return icmp_type, icmp_code, icmp_part[34:34 + 64]
    else:
        return icmp_type, icmp_code, icmp_part[2:]


def receive_ping(client_socket, packet_id, packet_seq):
    time_left = TIMEOUT
    time_start = time()

    while time_left > 0:
        time_in_select = time()
        ready = select([client_socket], [], [], time_left)
        time_in_select = time() - time_in_select

        if not ready[0]:
            return time() - time_start, PingError.OPERATION_TIMEOUT

        time_received = time()
        recv, _ = client_socket.recvfrom(1024)
        p_type, p_code, p_other = parse_icmp_packet(recv)

        if p_type == ICMP_ECHO_REPLY and p_code == 0:
            p_checksum, p_id, p_seq, p_data = p_other
            if p_id == packet_id and p_seq == packet_seq and checksum(
                    struct.pack("bbHHh", p_type, p_code, 0, p_id, p_seq) + p_data, False) + p_checksum == 0xffff:
                return time_received - time_start, None
        elif p_type == ICMP_DESTINATION_UNREACHABLE:
            _, _, (_, p_id, p_seq, _) = parse_icmp_packet(p_other)
            if p_id == packet_id and p_seq == packet_seq:
                return time_received - time_start, PingError(p_code)

        time_left -= time_in_select

    return time() - time_start, PingError.OPERATION_TIMEOUT


def send_ping(client_socket, dest_addr, packet_id, packet_seq):
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, 0, packet_id, packet_seq)
    data = struct.pack("d", time())
    csum = checksum(header + data)
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, csum, packet_id, packet_seq)
    packet = header + data
    client_socket.sendto(packet, (dest_addr, 1))


def do_ping(dest_addr, seq):
    client_socket = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP)
    packet_id = os.getpid() & 0xffff
    send_ping(client_socket, dest_addr, packet_id, seq)
    delay, err = receive_ping(client_socket, packet_id, seq)
    client_socket.close()
    return delay, err


def ping(host, times):
    global seq
    dest = gethostbyname(host)
    print(f'PING {host} ({dest})')
    while 1:
        seq += 1
        delay, err = do_ping(dest, seq)
        delay *= 1000
        if err is None:
            times.append(delay)
            print(f'Received ICMP echo reply from {dest}: icmp_seq={seq} time={round(delay, 3)} ms')
        else:
            print(f'Error occurred: {err.name}')
        sleep(1)


def avg(arr):
    return sum(arr) / len(arr)


def std(arr):
    return (sum([x ** 2 for x in arr]) / len(arr) - (sum(arr) / len(arr)) ** 2) ** 0.5


seq = 0
times = []
common_start = time()

try:
    ping(args.DESTINATION, times)
except KeyboardInterrupt:
    print()
    time_passed = (time() - common_start) * 1000
    print(f'{seq} packets transmitted, {len(times)} packets received, {round((1 - len(times) / seq) * 100)}% packet loss, time {round(time_passed)}ms')
    if len(times) > 0:
        print(f'rtt min/avg/max/mdev = {round(min(times), 3)}/{round(avg(times), 3)}/{round(max(times), 3)}/{round(std(times), 3)} ms')
