from GameScripts import Interfaz

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), os.path.pardir)))
from TcpScripts.client import Client
from TcpScripts.ClaseCliente import Cliente

from GameScripts.CartaScripts.Carta import *

cliente : Client = None

mano = []

def enviar_mensaje(msg):
    cliente.send_message(msg, "texto")

def on_server_close():
    pass

def on_message_recived(msg, type_of_msg):
    if type_of_msg == "texto":
        if isinstance(msg, Carta):
            mano.append(msg)
            Interfaz.mostrarMensaje("La carta recibida es el "+ msg.valor + " de " + msg.palo)
        else: 
            Interfaz.mostrarMensaje(msg)
        
    elif type_of_msg == "peticion":
        Interfaz.mostrarMensaje(msg)
        enviar_mensaje(Interfaz.recibe_respuesta())


def start():
    global cliente
    cliente = Client()

    cliente.events.on_server_close += on_server_close
    cliente.events.on_message_recived += on_message_recived