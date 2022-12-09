import socket
import threading
from node import Node
import clear as cl


HEADER = 64
PORT = 5050
SERVER = '192.168.100.13'
IP_ADDRESS = socket.gethostbyname(socket.gethostname())
DISCONNECT_MSG = "!disconn"
FORMAT = "ascii"


# Enter and check client information
valid = False
while not valid:
    try:
        valid = True
        # Enter client info
        peer_port = int(input("Enter your port: "))
        peer_name = input("Enter your name: ")
        # Connect to server
        peer = Node(IP_ADDRESS, peer_port, peer_name)
    # Port has already been used
    except OSError:
        valid = False
        print('[OS Error] This port has already been used.')
    # Entered port not a number
    except ValueError:
        valid = False
        print('[Value Error] Port must be a number. Try again.')

# Let client listen connections 
recv_thread = threading.Thread(target=peer.listen)
recv_thread.start()


# Main working section 
while True: 
    print('Option [1]: Connect to another client')
    print('Option [2]: Chat with a connected client')
    print('--------------------------------------')
    try:
        user_option = int(input('Choose your option: '))
    except ValueError:
        user_option = 'Value Error'
        
    # Work with each option 
    cl.clear()
    if user_option == 'Value Error':
        print('[Value Error] Please enter a number\n')

    elif user_option == 1:
        user_ip = input('Enter IP address to connect to: ')
        user_port = int(input('Enter port to connect to: '))
        conn = peer.connect(user_ip, user_port)

    elif user_option == 2:
        print(peer.all_names())
        user_name = input("Enter the client name to chat to: ")
        index = peer.all_names().index(user_name)
        conn = peer.all_nodes()[index]
        
        while conn in peer.all_nodes():
            msg = input('say sth: ')
            peer.send(conn, msg)

        conn.close()

    else:
        print('[Error] Invalid number. Please try again.\n')