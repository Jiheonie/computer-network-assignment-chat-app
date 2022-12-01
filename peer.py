import socket
import threading
from node import Node

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
DISCONNECT_MSG = "!disconn"
FORMAT = "ascii"


peer_port = int(input("Enter your port: "))
peer_name = input("Enter your name: ")
peer = Node(SERVER, peer_port, peer_name)
recv_thread = threading.Thread(target=peer.listen)
recv_thread.start()

while True: 
    print('Option [1]: Connect to another client')
    print('Option [2]: Chat with a connected client')
    print('--------------------------------------')
    user_option = int(input('Choose your option: '))
    # .....
    if user_option == 1:
        user_ip = input('Enter IP address to connect to: ')
        user_port = int(input('Enter port to connect to: '))
        conn = peer.connect(user_ip, user_port)

    if user_option == 2:
        print(peer.all_names())
        user_name = input("Enter the client name to chat to: ")
        index = peer.all_names().index(user_name)
        conn = peer.all_nodes()[index]
        
        while conn in peer.all_nodes():
            msg = input('say sth: ')
            peer.send(conn, msg)

        conn.close()
