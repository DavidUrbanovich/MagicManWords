import socket
import ssl
import threading

from scapy.layers.dns import DNSQR, DNS
from scapy.layers.inet import IP, TCP, UDP
from scapy.sendrecv import sniff, send

from Utils import check_connection

port = 0
host = 'localhost'
shutdown = False


def handle_communication():
    # Send Receiver Socket Information.
    # client_sender_socket.write(bytes(str(new_port), 'utf-8'))

    alias = input("Name: ")

    ip, new_port = client_receiver_socket.getsockname()
    p = IP(dst=server[0]) / TCP(dport=server[1]) \
        / DNS(rd=1, qd=DNSQR(qname=str(new_port)))
    send(p, verbose=0)

    print("Please Enter Your Messages!\n")
    message = input("")

    while message != 'q':
        if message != '':
            p = IP(dst=server[0]) / TCP(dport=server[1]) \
                / DNS(rd=1, qd=DNSQR(qname=(alias + ": " + message)))
            send(p, verbose=0)
            # client_sender_socket.write(bytes(alias + ": " + message, 'utf-8'))
        message = input("")


def incoming_data_handler(thread_name, sock):
    def receive_data():
        def get_data(pkt: IP):
            print(pkt[UDP].dport, sock.getsockname()[1])
            if pkt[UDP].dport == sock.getsockname()[1]:
                print(str(pkt[DNSQR].qname.decode('utf-8')))

        return get_data

    sniff(filter=f"udp port {sock.getsockname()[1]} and ip dst {sock.getsockname()[0]}", prn=receive_data())


def close_connection():
    global shutdown
    shutdown = True

    rT.join()
    client_sender_socket.close()
    client_receiver_socket.close()


server = ('127.0.0.1', 5000)

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

rT = threading.Thread(target=incoming_data_handler, args=("receive_thread", client_receiver_socket))
rT.start()

handle_communication()
close_connection()
