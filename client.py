import socket
import threading

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
DISCONNECT_MSG = "!disconn"
FORMAT = "ascii"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))


chat_still = True

def send():
    global chat_still
    while chat_still:
        msg = input()
        if msg == DISCONNECT_MSG:
            chat_still = False

        client.send(msg.encode(FORMAT))


def receive():
    global chat_still
    while chat_still:
        msg = client.recv(HEADER).decode(FORMAT)
        print(msg)
    
        

receive_thread = threading.Thread(target=receive)
receive_thread.start()

send_thread = threading.Thread(target=send)
send_thread.start()




