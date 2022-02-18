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

nombre_jugador : str = None

def add_carta_mano(carta: Carta):
    Interfaz.draw_hand_card(carta.to_string())
    print("add carta to mano")

def add_carta_vira(carta: Carta):
    Interfaz.draw_vira(carta.to_string())
    print("add vira", nombre_jugador)

def add_carta_sec_vira(carta: Carta):
    Interfaz.draw_sec_vira(carta.to_string())
    print("add sec vira", nombre_jugador)

def jugar_carta(msg):
    if msg[2] == nombre_jugador:
        if msg[1] == "up":
            Interfaz.card_to_selected_up(msg[3].to_string())
        elif msg[1] == "down":
            Interfaz.card_to_selected_down(msg[3].to_string())
    else:
        if msg[1] == "up":
            Interfaz.another_card_to_selected_up(msg[3].to_string(), msg[2])
        elif msg[1] == "down":
            Interfaz.another_card_to_selected_down(msg[2])

def set_jugador(nombre):
    global nombre_jugador
    nombre_jugador = nombre

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
            elif msg[0] == "set sec vira":
                if isinstance(msg[1], Carta):
                    add_carta_sec_vira(msg[1])
                else:
                    print("wtf")
            elif msg[0] == "jugar carta":
                jugar_carta(msg)
            elif msg[0] == "update points":
                Interfaz.update_points(msg[1])
            elif msg[0] == "update on play points":
                Interfaz.update_on_play_points(msg[1])
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
        if msg[0] == "ACTION":
            enviar_mensaje((Interfaz.choose_action(msg[1], msg[2]), nombre_jugador))
        elif msg[0] == "CARD":
            card_name: str = Interfaz.select_hand_card()
            enviar_mensaje((Carta(card_name.split(" ")[0], card_name.split(" ")[2]), nombre_jugador))
        elif msg[0] == "POPUP":
            res = Interfaz.make_election_popup("envio", msg[1], msg[2])
            enviar_mensaje((res, nombre_jugador))
        else:
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