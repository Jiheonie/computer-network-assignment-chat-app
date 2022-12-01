import socket
import threading
import re

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
DISCONNECT_MSG = "!disconn"
FORMAT = "ascii"
NAME_PATTERN = "\#NAME\:\s"

class Node:
    def __init__(self, host, port, name) -> None:
        self.host = host
        self.port = port
        self.name = name

        # connect
        self.nodes_out = []
        self.addrs_out = []
        self.names_out = ['server']

        # listen
        self.nodes_in = []
        self.addrs_in = []
        self.names_in = []

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.connect(SERVER, PORT)


    def connect(self, ip_addr, port):
        # Like a client in client-server
        # initialize nodes out 
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((ip_addr, port))
        self.nodes_out.append(conn)
        self.addrs_out.append((ip_addr, port))
        name_msg = f"#NAME: {self.name}"
        self.send_node_out(conn, name_msg)
        recv_thread = threading.Thread(target=self.recv_node_out, args=(conn,))
        recv_thread.start()
        return conn


    def listen(self):
        # Like server in client-server
        # receive connection from node in
        self.server_socket.listen()
        while True:
            (conn, addr) = self.server_socket.accept()
            self.nodes_in.append(conn)
            self.addrs_in.append(addr)
            name_msg = f"#NAME: {self.name}"
            self.send_node_in(conn, name_msg)
            recv_thread = threading.Thread(target=self.recv_node_in, args=(conn,))
            recv_thread.start()


    def all_nodes(self):
        return self.nodes_out + self.nodes_in

    
    def all_addrs(self):
        return self.addrs_out + self.addrs_in


    def all_names(self):
        return self.names_out + self.names_in


    def get_name(self, conn):
        index = self.all_nodes().index(conn)
        return self.all_names()[index]

            
    def recv_node_in(self, conn):
        # handle and receive message from a node in 
        while conn in self.nodes_in:
            recv_msg = conn.recv(HEADER).decode(FORMAT)
            if recv_msg:
                self.recv_msg(conn, recv_msg)

        conn.close()

    
    def recv_node_out(self, conn):
        while conn in self.nodes_out:
            recv_msg = conn.recv(HEADER).decode(FORMAT)
            if recv_msg:
                self.recv_msg(conn, recv_msg)

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


    def recv_msg(self, conn, recv_msg):
        match = re.search(NAME_PATTERN, recv_msg)
        if match:
            self.recv_name(conn, recv_msg)
        elif recv_msg == DISCONNECT_MSG:
            print(f'[{self.get_name(conn)}] disconnected')
            self.nodes_out.remove(conn)  
        else:   
            self.display_msg(conn, recv_msg) 
            
    
    def display_msg(self, conn, recv_msg):
        name = self.get_name(conn)
        print(f'\n[{name}] {recv_msg}') 

    
    def recv_name(self, conn, msg):
        split_msg = msg.split(": ")
        if conn in self.nodes_out:
            self.names_out.append(split_msg[1])
        else:
            self.names_in.append(split_msg[1])

