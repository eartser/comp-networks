BATCH_SIZE = 1024


def split_data(data):
    return [data[i:i + BATCH_SIZE] for i in range(0, len(data), BATCH_SIZE)]


def build_ack(index):
    return bytes([index]) + b'ACK'


def build_packet(data, index):
    return bytes([index]) + data.encode()


def parse_packet(packet):
    return packet[0], packet[1:].decode()


def read_file(filepath):
    with open(filepath) as file:
        return file.read()


def write_file(filepath, data):
    with open(filepath, 'wt') as file:
        return file.write(data)
