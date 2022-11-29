import socket
import threading

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
DISCONNECT_MSG = "!disconn"
FORMAT = "ascii"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER, PORT))

connections = []
accounts = []

def broadcast(msg):
    for conn in connections:
        conn.send(msg.encode(FORMAT))


def handle_client(conn, addr):
    welcome_msg = f"[NEW CONNECTION] {addr} is connected."
    # broadcast(welcome_msg)
    print(welcome_msg)

    connected = True
    while connected:
        recv_msg = conn.recv(HEADER).decode(FORMAT)
        if recv_msg:
            print(recv_msg)
            if recv_msg == DISCONNECT_MSG:
                connected = False
                print(f'[{addr}] DISCONNECTED')
                connections.remove(conn)    
            else:   
                broadcast_msg = f'[{addr}] {recv_msg}'
                print(broadcast_msg)
                # broadcast(broadcast_msg)

    conn.close()


def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        (conn, addr) = server.accept()
        connections.append(conn)
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start() 
        print(f"[ACTIVE CONNECTION] {threading.active_count() - 1}")




print('[STARTING] server is starting...')
start()
