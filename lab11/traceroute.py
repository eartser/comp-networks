import argparse
import os
import struct
from enum import Enum
from select import select
from socket import *
from time import time


parser = argparse.ArgumentParser()
parser.add_argument('DESTINATION', type=str)
parser.add_argument('--N', default=3)
parser.add_argument('--TIMEOUT', type=int, default=5)
args = parser.parse_args()

ICMP_ECHO_REPLY = 0
ICMP_DESTINATION_UNREACHABLE = 3
ICMP_ECHO_REQUEST = 8
ICMP_TIME_EXCEEDED = 11

TIMEOUT = args.TIMEOUT / args.N
N = args.N


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
    elif icmp_type in [ICMP_DESTINATION_UNREACHABLE, ICMP_TIME_EXCEEDED]:
        return icmp_type, icmp_code, icmp_part[34:34 + 64]
    else:
        return icmp_type, icmp_code, icmp_part[2:]


def receive_ping(client_socket, packet_id, packet_seq):
    time_left = TIMEOUT
    time_start = time()

    addr = None

    while time_left > 0:
        time_in_select = time()
        ready = select([client_socket], [], [], time_left)
        time_in_select = time() - time_in_select

        if not ready[0]:
            return time() - time_start, (ICMP_DESTINATION_UNREACHABLE, -1), addr

        time_received = time()
        recv, addr = client_socket.recvfrom(1024)
        p_type, p_code, p_other = parse_icmp_packet(recv)

        if p_type == ICMP_ECHO_REPLY and p_code == 0:
            p_checksum, p_id, p_seq, p_data = p_other
            if p_id == packet_id and p_seq == packet_seq and checksum(
                    struct.pack("bbHHh", p_type, p_code, 0, p_id, p_seq) + p_data, False) + p_checksum == 0xffff:
                return time_received - time_start, (p_type, p_code), addr
        elif p_type == ICMP_TIME_EXCEEDED and p_code == 0:
            return time_received - time_start, (p_type, p_code), addr
        elif p_type == ICMP_DESTINATION_UNREACHABLE:
            _, _, (_, p_id, p_seq, _) = parse_icmp_packet(p_other)
            if p_id == packet_id and p_seq == packet_seq:
                return time_received - time_start, (p_type, p_code), addr

        time_left -= time_in_select

    return time() - time_start, (ICMP_DESTINATION_UNREACHABLE, -1), addr


def send_ping(client_socket, dest_addr, packet_id, packet_seq):
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, 0, packet_id, packet_seq)
    data = struct.pack("d", time())
    csum = checksum(header + data)
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, csum, packet_id, packet_seq)
    packet = header + data
    client_socket.sendto(packet, (dest_addr, 1))


def do_ping(dest_addr, seq, ttl):
    client_socket = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP)
    client_socket.setsockopt(IPPROTO_IP, IP_TTL, ttl)
    packet_id = os.getpid() & 0xffff
    send_ping(client_socket, dest_addr, packet_id, seq)
    delay, type_code, addr = receive_ping(client_socket, packet_id, seq)
    client_socket.close()
    return delay, type_code, addr


def traceroute(host):
    global seq
    dest = gethostbyname(host)
    ttl = 0
    flag = False
    print(f'traceroute to {host} ({dest})')
    while 1:
        ttl += 1
        delays = []
        cur_addr = None
        for _ in range(N):
            seq += 1
            delay, (resp_type, resp_code), addr = do_ping(dest, seq, ttl)
            delay *= 1000
            if cur_addr is None:
                cur_addr = addr
            if resp_type == ICMP_DESTINATION_UNREACHABLE:
                delays.append('*')
            elif resp_type in [ICMP_ECHO_REPLY, ICMP_TIME_EXCEEDED]:
                delays.append(f'{round(delay, 3)} ms')
                if resp_type == ICMP_ECHO_REPLY:
                    flag = True
        if cur_addr is None:
            print(f'{ttl}  ' + ' '.join(delays))
            continue
        try:
            hostname = gethostbyaddr(cur_addr[0])[0]
        except herror:
            hostname = cur_addr[0]
        print(f'{ttl}  {hostname} ({cur_addr[0]})  ', end='')
        if set(delays) == set('*'):
            print(' '.join(delays))
        else:
            print('  '.join(delays))
        if flag:
            break


seq = 0
traceroute(args.DESTINATION)
