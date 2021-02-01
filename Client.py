import socket
import ssl
import threading
from scapy.layers.dns import DNS, DNSQR
from scapy.layers.inet import IP, UDP
from scapy.sendrecv import sr1

from Utils import check_connection

port = 0
host = 'localhost'
shutdown = False


def get_server_ip(dns_server_ip, dns_query_name):
    dns_req = IP(dst=dns_server_ip) / \
              UDP(dport=53) / \
              DNS(rd=1, qd=DNSQR(qname=dns_query_name))
    answer = sr1(dns_req, verbose=0)
    return str(answer[DNS].an[0].rdata)


def handle_communication():
    # Send Receiver Socket Information.
    ip, new_port = client_receiver_socket.getsockname()
    client_sender_socket.write(bytes(str(new_port), 'utf-8'))

    alias = input("Name: ")

    print("Please Enter Your Messages!\n")
    message = input("")

    while message != 'q':
        if message != '':
            check_connection(server[0])
            client_sender_socket.write(bytes(alias + ": " + message, 'utf-8'))
        message = input("")


def receive_data(name, sock):
    while not shutdown:
        try:
            data, address = sock.recvfrom(1024)
            print(str('\r' + data.decode('utf-8')))
        except socket.error as err:
            print(err)


def close_connection():
    global shutdown
    shutdown = True

    rT.join()
    client_sender_socket.close()
    client_receiver_socket.close()


server = (get_server_ip('127.0.0.1', 'david.server.com'), 5000)

context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
context.verify_mode = ssl.CERT_REQUIRED
context.check_hostname = True
context.load_verify_locations("./assets/cert.pem")

client_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP
client_sender_socket = context.wrap_socket(client_sender_socket, server_hostname="david.server.com", server_side=False)
client_sender_socket.bind((host, port))
client_sender_socket.connect(server)

client_receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
client_receiver_socket.bind((host, port))
client_receiver_socket.setblocking(True)

rT = threading.Thread(target=receive_data, args=("receive_thread", client_receiver_socket))
rT.start()

handle_communication()
close_connection()
