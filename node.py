import socket
import threading
import re


HEADER = 2048
PORT = 5050
SERVER = '172.16.3.158'
DISCONNECT_MSG = "!exit"
FORMAT = "ascii"
NAME_PATTERN = "\#NAME\:\s"
CONNS_PATTERN = "conns\:\s"
ADDRS_PATTERN = "addrs\:\s"
NAMES_PATTERN = "names\:\s"


class Node:
    def __init__(self, host, port, name) -> None:
        self.host = host
        self.port = port
        self.name = name

        self.available_users = []
        
        # connect
        self.nodes_out = []
        self.addrs_out = []
        self.names_out = ['server']

        # listen
        self.nodes_in = []
        self.addrs_in = []
        self.names_in = []

        self.messages = ['abcd']

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

    
    def connect_auto(self, name):
        connected = False
        if name in self.all_names():
            connected = True
        if not connected:
            pass
            


    def request_server(self, command):
        if command == "!online":
            self.send_by_name("server", "!online")
            # recv_msg = str(self.recv_by_name("server"))
            recv_msg = str(self.nodes_out[0].recv(HEADER).decode(FORMAT))
            print(recv_msg)
            print(recv_msg)
            # tach danh sach ra
            self.available_users = eval(recv_msg)  
            print(self.available_users)
            print(len(self.available_users))
                        

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


    def find_name_by_conn(self, conn):
        index = self.all_nodes().index(conn)
        return self.all_names()[index]


    def find_conn_by_name(self, name):
        index = self.all_names().index(name)
        return self.all_nodes()[index]

            
    def recv_node_in(self, conn):
        while conn in self.nodes_in:
            recv_msg = conn.recv(HEADER).decode(FORMAT)
            if recv_msg:
                self.recv_msg(conn, recv_msg)


    
    def recv_node_out(self, conn):
        name = self.find_name_by_conn(conn)
        while conn in self.nodes_out and name != "server":
            recv_msg = conn.recv(HEADER).decode(FORMAT)
            if recv_msg:
                self.recv_msg(conn, recv_msg)

    
    def recv_by_name(self, name):
        conn = self.find_conn_by_name(name)
        return conn.recv(HEADER).decode(FORMAT)


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

    
    def send_by_name(self, name, msg):
        if name in self.all_names():
            conn = self.find_conn_by_name(name)
            self.send(conn, msg)
        else:
            print("This name is not available")


    def recv_msg(self, conn, msg):
        match = re.search(NAME_PATTERN, msg)
        if match:
            self.recv_name(conn, msg)
        elif msg == DISCONNECT_MSG:
            self.disconnect(conn)
        else:   
            self.display_msg(conn, msg) 
            
    
    def display_msg(self, conn, recv_msg):
        name = self.find_name_by_conn(conn)
        print(f'\n[{name}] {recv_msg}') 
        # pass


    def disconnect(self, conn):
        print(f'[{self.find_name_by_conn(conn)}] disconnected')
        self.nodes_out.remove(conn)  

    
    def recv_name(self, conn, msg):
        split_msg = msg.split(": ")
        if conn in self.nodes_out:
            self.names_out.append(split_msg[1])
        else:
            self.names_in.append(split_msg[1])


