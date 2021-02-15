import socket
import ssl
import time
import _thread

from scapy.layers.dns import DNS, DNSQR
from scapy.layers.inet import IP, UDP
from scapy.sendrecv import send, sniff

host = '127.0.0.1'
port = 5000
clients = []
clients_to_remove = []


class Client:
    def __init__(self, sender_socket, receiver_socket):
        self.sender_socket = sender_socket
        self.receiver_socket = receiver_socket

    def __str__(self):
        return str(self.sender_socket) + ' ' + str(self.receiver_socket)


def handle_new_client(client_socket, address):
    global clients
    client_port = -1

    client_socket = ssl.wrap_socket(client_socket, server_side=True, keyfile="./assets/nokey.pem",
                                    certfile="./assets/cert.pem", cert_reqs=ssl.CERT_NONE,
                                    ssl_version=ssl.PROTOCOL_SSLv23)

    clients.append(Client(address, (address[0], -1)))
    sniff(filter=f"tcp port {server_receiver_socket.getsockname()[1]} and ip dst "
                 f"{server_receiver_socket.getsockname()[0]}", prn=handle_incoming_data(address))


def handle_incoming_data(address):
    def get_data(pkt: IP):
        try:
            client_message = pkt[DNSQR].qname[:-1].decode('utf-8')

            add_new_client = False
            for client in clients:
                if client.receiver_socket[1] == -1 and client.sender_socket == address:
                    add_new_client = True
                    client.receiver_socket = (client.receiver_socket[0], int(client_message))

            if not add_new_client:
                print(time.ctime(time.time()) + str(address) + " => " + str(client_message))

                for client in clients:
                    if client.sender_socket != address:
                        try:
                            if client.receiver_socket[1] != -1:
                                p = IP(dst=client.receiver_socket[0]) / UDP(dport=client.receiver_socket[1]) \
                                    / DNS(rd=1, qd=DNSQR(qname=client_message))
                                print(client.receiver_socket[1])
                                send(p, verbose=0)
                                print("Message was sent to", client)
                        except socket.error as err:
                            print(err)
        except socket.error as err:
            print(err)
            clients_to_remove.append(address)
    return get_data


def handle_server_commands():
    while running:
        command = input("Please Enter 'Shutdown' To Stop The Server!\n")
        if command.lower() == 'shutdown':
            shutdown_server()


def handle_closed_connections():
    global clients
    global clients_to_remove

    while True:
        removed_clients = []
        for removed_client in clients_to_remove:
            clients = [client for client in clients if client.sender_socket != removed_client]
            removed_clients.append(removed_client)

        if len(removed_clients) > 0:
            clients_to_remove = [client for client in clients_to_remove if client not in removed_clients]


def shutdown_server():
    global running

    running = False
    server_sender_socket.close()
    server_receiver_socket.close()


# Handles Outgoing Data
server_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_sender_socket.setblocking(False)

# Handles Incoming Data
server_receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_receiver_socket.bind((host, port))
server_receiver_socket.listen(5)
server_receiver_socket.setblocking(True)

running = True
print("Server Started.")
_thread.start_new_thread(handle_server_commands, ())
_thread.start_new_thread(handle_closed_connections, ())

while running:
    try:
        _thread.start_new_thread(handle_new_client, server_receiver_socket.accept())
        print("New Connection Was Made.")
    except socket.error as accept_err:
        print(accept_err)
