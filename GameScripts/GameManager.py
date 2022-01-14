import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), os.path.pardir)))
from TcpScripts.server import Server
from TcpScripts.ClaseCliente import Cliente


def on_message_recived(msg, type_of_msg: str, client: Cliente):
    pass

def on_client_exit(client: Cliente):
    pass

def on_client_connect(client: Cliente):
    pass

server = Server()

server.events.on_message_recived += on_message_recived
server.events.on_client_exit += on_client_exit
server.events.on_client_connect += on_client_connect
