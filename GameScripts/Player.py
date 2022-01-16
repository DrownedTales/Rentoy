from GameScripts import Interfaz

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), os.path.pardir)))
from TcpScripts.client import Client
from TcpScripts.ClaseCliente import Cliente

from GameScripts.CartaScripts.Carta import *
from GameScripts.ClasePlayer import Jugador

cliente : Client = None

mano = []
vira : Carta = None
jugador : Jugador = None

def add_carta_mano(carta: Carta):
    mano.append(carta)
    Interfaz.mostrarMensaje("La carta recibida es el " + carta.to_string())

def add_carta_vira(carta: Carta):
    vira = carta
    Interfaz.mostrarMensaje("La vira será el " + carta.to_string())

def reset_ronda(n_rondas):
    mano = []
    vira = None
    Interfaz.mostrarMensaje("Comenzará la ronda " + str(n_rondas))

def set_jugador(participante):
    global jugador
    jugador = participante

def mostrar_vira(carta: Carta):
    Interfaz.mostrarMensaje(carta)

def enviar_mensaje(msg):
    cliente.send_message(msg, "data")

def on_server_close():
    Interfaz.mostrarMensaje("el servidor se ha cerrado")

def on_message_recived(msg, type_of_msg):
    if type_of_msg == "data":
        #hace falta diferenciar entre carta y vira. Tarea para ti pablo. No tienes que tocar nada de lo que hay en TCP
        if isinstance(msg, Carta):
            if vira == Carta:
                add_carta_mano(msg)
            else:
                add_carta_vira(msg)
        elif isinstance(msg, tuple):
            if msg[0] == "resetear ronda":
                reset_ronda(msg[1])
            elif msg[0] == "set jugador":
                set_jugador(msg[1])
        else:
            Interfaz.mostrarMensaje("recibido: " + str(msg))
        
    elif type_of_msg == "peticion":
        Interfaz.mostrarMensaje(msg)
        enviar_mensaje(Interfaz.recibe_respuesta())

    elif type_of_msg == "eleccion":
        Interfaz.espera_eleccion(msg[0], msg[1])(jugador)



def start():
    global cliente
    cliente = Client()

    cliente.events.on_server_close += on_server_close
    cliente.events.on_message_recived += on_message_recived