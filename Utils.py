import time
import random
import struct
import socket

from scapy.layers.inet import IP, ICMP, UDP
from icmplib import ICMPv4Socket, ICMPRequest, PID, TimeoutExceeded, \
                    DestinationUnreachable, TimeExceeded, ICMPLibError
from scapy.sendrecv import sr1, send


def check_connection(address, timeout=2, request_id=PID):
    sock = ICMPv4Socket()
    request = ICMPRequest(destination=address, id=request_id, sequence=1)

    try:
        sock.send(request)
        reply = sock.receive(request, timeout)
        reply.raise_for_status()

    except TimeoutExceeded as err:
        print(err)

    except DestinationUnreachable as err:
        print(err)

    except TimeExceeded as err:
        print(err)

    except ICMPLibError as err:
        print(err)


def checksum(source_string):
    # I'm not too confident that this is right but testing seems to
    # suggest that it gives the same answers as in_cksum in ping.c.
    sum = 0
    count_to = (len(source_string) // 2) * 2
    count = 0
    while count < count_to:
        this_val = source_string[count + 1] * 256 + source_string[count]
        sum = sum + this_val
        sum = sum & 0xffffffff  # Necessary?
        count = count + 2
    if count_to < len(source_string):
        sum = sum + source_string[len(source_string) - 1]
        sum = sum & 0xffffffff  # Necessary?
    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    # Swap bytes. Bugger me if I know why.
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def create_packet(data, id):
    """Create a new echo request packet based on the given "id"."""
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    header = struct.pack('bbHHh', 8, 0, 0, id, 1)
    # Calculate the checksum on the data and the dummy header.
    my_checksum = checksum(header + data)
    # Now that we have the right checksum, we put that in. It's just easier
    # to make up a new header than to stuff it into the dummy.
    header = struct.pack('bbHHh', 8, 0,
                         socket.htons(my_checksum), id, 1)
    return header + data


def packet(data, timeout=1):
    packet_id = int((id(timeout) * random.random()) / 65535)
    return create_packet(data, packet_id)
