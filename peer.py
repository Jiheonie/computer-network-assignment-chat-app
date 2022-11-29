import socket
import threading

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
# SERVER = '192.168.100.13'
DISCONNECT_MSG = "!disconn"
FORMAT = "ascii"

class Node:
    def __init__(self, host, port) -> None:
        self.host = host
        self.port = port
        self.nodes_out = []
        self.nodes_in = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.connect(SERVER, PORT)


    def connect(self, ip_addr, port):
        # Like a client in client-server
        # initialize nodes out 
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((ip_addr, port))
        self.nodes_out.append(conn)
        recv_thread = threading.Thread(target=self.recv_node_out, args=(conn, (ip_addr, port)))
        recv_thread.start()
        return conn


    def listen(self):
        # Like server in client-server
        # receive connection from node in
        self.server_socket.listen()
        while True:
            (conn, addr) = self.server_socket.accept()
            self.nodes_in.append(conn)
            recv_thread = threading.Thread(target=self.recv_node_in, args=(conn, addr))
            recv_thread.start()


    def all_nodes(self):
        return self.nodes_in + self.nodes_out

            
    def recv_node_in(self, conn, addr):
        # handle and receive message from a node in 
        while conn in self.nodes_in:
            recv_msg = conn.recv(HEADER).decode(FORMAT)
            if recv_msg:
                # print(recv_msg)
                if recv_msg == DISCONNECT_MSG:
                    print(f'[{addr}] DISCONNECTED')
                    self.nodes_in.remove(conn)  
                else:   
                    print(f'{addr} {recv_msg}')

        conn.close()

    
    def recv_node_out(self, conn, addr):
        while conn in self.nodes_out:
            recv_msg = conn.recv(HEADER).decode(FORMAT)
            if recv_msg:
                # print(recv_msg)
                if recv_msg == DISCONNECT_MSG:
                    print(f'[{addr}] DISCONNECTED')
                    self.nodes_out.remove(conn)  
                else:   
                    print(f'{addr} {recv_msg}') 

        conn.close()


    def send_node_out(self, conn, msg):
        if msg == DISCONNECT_MSG:
            self.nodes_out.remove(conn)

        conn.send(msg.encode(FORMAT))


    def send_node_in(self, conn, msg):
        if msg == DISCONNECT_MSG:
            self.nodes_in.remove(conn)

        conn.send(msg.encode(FORMAT))


    def send(self, conn, msg):
        if conn in self.nodes_in:
            self.send_node_in(conn, msg)
        if conn in self.nodes_out:
            self.send_node_out(conn, msg)



peer_port = int(input("Enter your port: "))
peer = Node(SERVER, peer_port)
recv_thread = threading.Thread(target=peer.listen)
recv_thread.start()

while True: 
    print('Option 1: Connect to another address')
    print('------------------------------------')
    user_option = int(input('Choose your option: '))
    # .....
    if user_option == 1:
        user_ip = input('Enter IP address connect to: ')
        user_port = int(input('Enter port connect to: '))
        conn = peer.connect(user_ip, user_port)
        while conn in peer.all_nodes():
            msg = input('say sth: ')
            peer.send(conn, msg)

        conn.close()
