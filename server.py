import socket
import threading

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
DISCONNECT_MSG = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER, PORT))


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} is connected.")

    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode("utf-8")
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode("utf-8")
            if msg == DISCONNECT_MSG:
                connected = False

            print(f'[{addr}] {msg}')
            conn.send("Message received.".encode("utf-8"))

    conn.close()


def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        (conn, addr) = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start() 
        print(f"[ACTIVE CONNECTION] {threading.active_count() - 1}")



print('[STARTING] server is starting...')
start()
