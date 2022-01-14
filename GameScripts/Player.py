import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), os.path.pardir)))
from TcpScripts.client import Client
from TcpScripts.ClaseCliente import Cliente


def on_server_close():
    pass

def on_message_recived(msg, type_of_msg):
    pass

server = Client()

server.events.on_server_close += on_server_close
server.events.on_message_recived += on_message_recived