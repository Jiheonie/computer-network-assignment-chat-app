import socket
import threading
import re


HEADER = 2048
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
DISCONNECT_MSG = "!exit"
FORMAT = "utf-8"
NAME_PATTERN = "\#NAME\:\s"
FILENAME_PATTERN = "\#FILENAME\:\s"
FILE_PATTERN = "\#FILE\:\s"


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

        self.messages = []

        self.filename = []

        self.working = True

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.connect(SERVER, PORT)
        self.send_info()


    def send_info(self):
        self.send_by_name("server", F"#ADDR: {self.host}: {self.port}")

        
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
        print(self.all_names())
        if name in self.all_names():
            connected = True
        if not connected:
            index = self.available_users[1].index(name)
            addr = self.available_users[0][index]
            ip = addr[0]
            port = addr[1]
            self.connect(ip, port)

            print(f"OK: {self.all_names()}")
            

    def request_server(self, command):
        if command == "!online":
            self.send_by_name("server", "!online")
            recv_msg = str(self.nodes_out[0].recv(HEADER).decode(FORMAT))
            # tach danh sach ra
            self.available_users = eval(recv_msg)  
        elif command == "!exit":
            for name in self.all_names():
                self.send_by_name(name, "!exit")
                        

    def listen(self):
        # Like server in client-server
        # receive connection from node in
        self.server_socket.listen()
        while self.working:
            (conn, addr) = self.server_socket.accept()
            self.nodes_in.append(conn)
            self.addrs_in.append(addr)
            name_msg = f"#NAME: {self.name}"
            self.send_node_in(conn, name_msg)
            recv_thread = threading.Thread(target=self.recv_node_in, args=(conn,))
            recv_thread.start()
            recv_thread.join()


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
            print(recv_msg)
            if recv_msg:
                self.recv_msg(conn, recv_msg)


    def recv_node_out(self, conn):
        try: 
            name = self.find_name_by_conn(conn)
        except IndexError:
            name = ""
        while conn in self.nodes_out and name != "server":
            
            recv_msg = conn.recv(HEADER).decode(FORMAT)
            print(recv_msg)
            if recv_msg:
                self.recv_msg(conn, recv_msg)

    
    def recv_by_name(self, name):
        conn = self.find_conn_by_name(name)
        return conn.recv(HEADER).decode(FORMAT)


    def send_node_out(self, conn, msg):
        if msg == DISCONNECT_MSG:
            self.remove_out(conn)
        conn.send(msg.encode(FORMAT))


    def send_node_in(self, conn, msg):
        if msg == DISCONNECT_MSG:
            self.remove_in(conn)
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
            for msg in self.messages:
                if msg == f"Not connected to {name}\n\n" or msg == "Not connected to anyone\n\n":
                    self.messages.remove(msg)
            return True

        print("This name is not available")
        if name == "No one chosen":
            self.messages.append("Not connected to anyone\n\n")
        else:
            self.messages.append(f"Not connected to {name}\n\n")
        return False


    def recv_msg(self, conn, msg):
        name_match = re.search(NAME_PATTERN, msg)
        filename_match = re.search(FILENAME_PATTERN, msg)
        file_match = re.search(FILE_PATTERN, msg)
        if name_match:
            self.recv_name(conn, msg)
            print(f"Connected: {self.all_names()}")
        elif filename_match:
            self.recv_filename(msg)
        elif file_match:
            self.recv_file(msg)
        elif msg == "!exit":
            name = self.find_name_by_conn(conn)
            self.messages.append(f"{name} disconnected")
            self.disconnect(conn)
            print(self.all_names())
        else:   
            self.display_msg(conn, msg) 
            print(self.messages)
            
    
    def display_msg(self, conn, recv_msg):
        name = self.find_name_by_conn(conn)
        self.messages.append(f'[{name}]  {recv_msg}\n\n') 


    def disconnect(self, conn):
        print(f'[{self.find_name_by_conn(conn)}] disconnected')
        if conn in self.nodes_in:
            self.remove_in(conn)
        else:
            self.remove_out(conn)

    
    def recv_name(self, conn, msg):
        split_msg = msg.split(": ")
        if conn in self.nodes_out:
            self.names_out.append(split_msg[1])
        else:
            self.names_in.append(split_msg[1])


    def recv_filename(self, msg):
        split_msg = msg.split(": ")
        file_name_recved = split_msg[1]
        self.filename.append(f"#{file_name_recved}")
        print(self.filename)

    
    def recv_file(self, msg):
        split_msg = msg.split(": ")
        changed_filename = split_msg[1]
        if changed_filename in self.filename:
            print("received")
            data = split_msg[2]
            filename = changed_filename[1:]
            print(filename)
            with open(f"test_{filename}", "wb") as f:
                f.write(bytes(data))


    def remove_out(self, conn):
        index = self.nodes_out.index(conn)
        self.nodes_out.remove(conn)  
        self.addrs_out.pop(index)
        self.names_out.pop(index)


    def remove_in(self, conn):
        index = self.nodes_in.index(conn)
        self.nodes_in.remove(conn)  
        self.addrs_in.pop(index)
        self.names_in.pop(index)