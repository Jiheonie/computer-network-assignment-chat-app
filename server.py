import socket
import threading

import re

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
FORMAT = "ascii"
NAME_PATTERN = "\#NAME\:\s"


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


    def handle_client(self, conn, addr):
        connected = True
        while connected:
            recv_msg = conn.recv(HEADER).decode(FORMAT)
            if recv_msg:
                print(recv_msg)
                match = re.search(NAME_PATTERN, recv_msg)
                if match:
                    self.recv_name(recv_msg)
                elif recv_msg == "exit":
                    connected = False
                    print(f'[{addr}] DISCONNECTED')
                    self.conns.remove(conn)    
                elif recv_msg == "!online":   
                    online_list = str(self.online_users)
                    self.send(conn, online_list)

                    

        conn.close()


    def show_available_users(self):
        pass


    def start(self, ):
        self.host.listen()
        print(f"[LISTENING] Server is listening on {SERVER}")
        while True:
            (conn, addr) = self.host.accept()
            self.conns.append(conn)
            self.addrs.append(addr)
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start() 
            print(f"[ACTIVE CONNECTION] {threading.active_count() - 1}")



server = Server()
print('[STARTING] server is starting...')
server.start()
