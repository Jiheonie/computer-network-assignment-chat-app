import ui
import threading
import sys
import node
import socket


# NOTE: example: python main.py 8882 Hoang
my_ip = str(socket.gethostbyname(socket.gethostname()))
my_port = int(sys.argv[1])
my_name = str(sys.argv[2])


# NOTE: ask the admin who is running server for the server ip address
# server_ip = str(input("Enter server IP: "))
server_ip = '127.0.0.1'

peer = node.Node(my_ip, my_port, my_name, server_ip)
recv_thread = threading.Thread(target=peer.listen)
recv_thread.start()


app = ui.MainUi(node=peer)
app.after(500, app.show_mesage)

app.mainloop()


peer.working = False
peer.request_server("!exit")
print("exited!")