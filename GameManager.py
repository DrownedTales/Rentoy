import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), os.path.pardir)))
from TcpScripts.connectionManager import ConnectionManager

from GameScripts.ClasePlayer import Jugador

from GameScripts.CartaScripts.Mazo import *

N_JUGADORES = 1

jugadores = []

con_man : ConnectionManager = None

def __get_clientes_de(jugadores):
    clientes = []
    for jugador in jugadores:
        clientes.append(jugador.cliente)
    return clientes

def __establecer_jugador(nombre, cliente):
    print("nuevo jugador: " + nombre)
    jugadores.append(Jugador(nombre, cliente))


def comienzo_ronda(n_rondas):
    mazo = crear_mazo()

    vira: Carta = sacar_carta_aleatoria(mazo)

    con_man.enviar_mensaje(__get_clientes_de(jugadores), vira)


    for i in range(n_rondas):
        carta = sacar_carta_aleatoria(mazo)
        con_man.enviar_mensaje(__get_clientes_de(jugadores), carta)


def start():
    global con_man
    con_man = ConnectionManager()

    con_man.beginAcceptingConnections(lambda client : con_man.pedir_respuesta(client, "Escriba su nombre:", __establecer_jugador))

    global jugadores

    con_man.wait_until(lambda : len(jugadores) >= N_JUGADORES)

    con_man.stopAcceptingConnections()

    print("Listos para empezar...")

    comienzo_ronda(2)