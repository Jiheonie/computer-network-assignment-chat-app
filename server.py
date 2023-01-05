import socket
import threading

import re

HEADER = 2048
PORT = 5050
SERVER = '127.0.0.1'
FORMAT = "latin-1"
NAME_PATTERN = "\#NAME\:\s"
ADDR_PATTERN = "\#ADDR\:\s"


class Server:
    def __init__(self) -> None:
        self.host = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host.bind((SERVER, PORT))

        self.conns = []
        self.addrs = []
        self.names = []

        self.online_users = [self.addrs, self.names]


    def send(self, conn, msg):
        conn.send(msg.encode(FORMAT))


    def recv_name(self, msg):
        split_msg = msg.split(": ")
        self.names.append(split_msg[1])


    def recv_addr(self, msg):
        split_msg = msg.split(": ")
        self.addrs.append((split_msg[1], int(split_msg[2])))


    def handle_client(self, conn, addr):
        connected = True
        while connected:
            recv_msg = conn.recv(HEADER).decode(FORMAT)
            if recv_msg:
                print(recv_msg)
                match_name = re.search(NAME_PATTERN, recv_msg)
                match_addr = re.search(ADDR_PATTERN, recv_msg)
                if match_name:
                    self.recv_name(recv_msg)
                elif match_addr:
                    self.recv_addr(recv_msg)
                elif recv_msg == "!exit":
                    connected = False
                    print(f'[{addr}] DISCONNECTED')
                    index = self.conns.index(conn)  
                    self.conns.remove(conn)  
                    self.addrs.pop(index)
                    self.names.pop(index)
                    self.online_users = [self.addrs, self.names]
                elif recv_msg == "!online":   
                    online_list = str(self.online_users)
                    self.send(conn, str(online_list))

        conn.close()


    def start(self, ):
        self.host.listen()
        print(f"[LISTENING] Server is listening on {SERVER}")
        while True:
            (conn, addr) = self.host.accept()
            self.conns.append(conn)
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start() 
            print(f"[ACTIVE CONNECTION] {threading.active_count() - 1}")



server = Server()
print('[STARTING] server is starting...')
server.start()
