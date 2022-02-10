from time import sleep
from GameScripts import Interfaz

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), os.path.pardir)))
from TcpScripts.client import Client
from TcpScripts.ClaseCliente import Cliente

from GameScripts.CartaScripts.Carta import *
from GameScripts.ClasePlayer import Jugador

cliente : Client = None
running: bool = False

mano = []
vira : Carta = None
nombre_jugador : str = None

def add_carta_mano(carta: Carta):
    mano.append(carta)
    #Interfaz.draw_hand_card(carta.to_string(), nombre_jugador)
    #lo de arriba es el final, esto es provisional
    Interfaz.draw_hand_card("test4", nombre_jugador)
    print("add carta to mano", nombre_jugador)

def add_carta_vira(carta: Carta):
    global vira
    vira = carta

    #Interfaz.set_vira(carta.to_string())
    #lo de arriba es el final, esto es provisional
    Interfaz.draw_vira("test5")
    print("add vira", nombre_jugador)

def mostrar_mano():
    Interfaz.mostrarMensaje(str(mano))

def reset_ronda(n_rondas):
    global mano
    global vira
    mano = []
    vira = None
    print("reset ronda")
    Interfaz.mostrarMensaje("Comenzará la ronda " + str(n_rondas))

def set_jugador(nombre):
    global nombre_jugador
    nombre_jugador = nombre

def mostrar_vira(carta: Carta):
    Interfaz.mostrarMensaje(carta)

def enviar_mensaje(msg):
    cliente.send_message(msg, "data")

def on_server_close():
    Interfaz.mostrarMensaje("el servidor se ha cerrado")

#estoy totalmente convencido de que esto no solo es feo sino disfuncional y un atentado contra la buena estructura de codigo y
#todo lo que yo defiendo. Dicho lo cual, se va a quedar asi
def on_message_recived(msg, type_of_msg):
    print("recived", msg)
    if type_of_msg == "data":
        if isinstance(msg, tuple):
            if msg[0] == "error":
                Interfaz.make_error_popup(msg[1], msg[2])
            elif msg[0] == "clear window":
                Interfaz.clear_window()
            elif msg[0] == "resetear ronda":
                reset_ronda(msg[1])
            elif msg[0] == "start game":
                Interfaz.start_game(msg[1], nombre_jugador)
            elif msg[0] == "set jugador":
                set_jugador(msg[1])
            elif msg[0] == "update waiting players":
                Interfaz.waiting_players(msg[1], msg[2])
            elif msg[0] == "update waiting teams":
                Interfaz.waiting_teams(msg[1])
            elif msg[0] == "add card":
                if msg[1] != nombre_jugador:
                    Interfaz.draw_hidden_card(msg[1])
            elif msg[0] == "add player card":
                if isinstance(msg[1], Carta):
                    add_carta_mano(msg[1])
                else:
                    print("wtf")
            elif msg[0] == "set vira":
                if isinstance(msg[1], Carta):
                    add_carta_vira(msg[1])
                else:
                    print("wtf")
        elif msg == "mostrar mano":
            mostrar_mano()
        else:
            Interfaz.mostrarMensaje("Game Manager: " + str(msg))
        
    elif type_of_msg == "peticion":
        Interfaz.clear_window()
        Interfaz.mostrarMensaje(msg)
        if nombre_jugador != None:
            enviar_mensaje((Interfaz.recibe_respuesta(), nombre_jugador))
        else:
            enviar_mensaje(Interfaz.recibe_respuesta())


    elif type_of_msg == "eleccion":
        Interfaz.clear_window()
        Interfaz.mostrarMensaje(msg[0])
        res = Interfaz.espera_eleccion(msg[1], msg[2])
        enviar_mensaje((res, nombre_jugador))



def start():
    global cliente
    global running
    if running:
        cliente.close_connection()
    cliente = Client()

    if not running:
        cliente.events.on_server_close += on_server_close
        cliente.events.on_message_recived += on_message_recived

    running = True