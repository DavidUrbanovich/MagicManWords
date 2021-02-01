import socket
import ssl
import time
import _thread

from Utils import check_connection

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

    run_thread = True
    while run_thread:
        try:
            client_message = client_socket.read(1024)

            if client_port == -1:
                client_port = client_message
                clients.append(Client(address, (address[0], int(client_port))))

            else:
                print(time.ctime(time.time()) + str(address) + " => " + str(client_message.decode('utf-8')))

                for client in clients:
                    if client.sender_socket != address:
                        try:
                            check_connection(client.receiver_socket[0])
                            server_sender_socket.sendto(client_message, client.receiver_socket)
                            print("Message was sent to", client)
                        except socket.error as err:
                            print(err)
        except socket.error as err:
            print(err)
            run_thread = False
            clients_to_remove.append(address)


def handle_server_commands():
    while running:
        command = input("Please Enter 'Shutdown' To Stop The Server!\n")
        if command == 'shutdown':
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
