import ui
import threading
import sys
import node

my_ip = str(sys.argv[1])
my_port = int(sys.argv[2])
my_name = str(sys.argv[3])

peer = node.Node(my_ip, my_port, my_name)
recv_thread = threading.Thread(target=peer.listen)
recv_thread.start()

app = ui.MainUi(node=peer)
app.after(500, app.show_mesage)

app.mainloop()

peer.working = False
peer.request_server("!exit")