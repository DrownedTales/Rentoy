import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), os.path.pardir)))
from TcpScripts.connectionManager import ConnectionManager

from GameScripts.ClasePlayer import Jugador

N_JUGADORES = 1

jugadores = []

con_man : ConnectionManager = None


def __establecer_jugador(nombre, cliente):
    print("nuevo jugador: " + nombre)
    jugadores.append(Jugador(nombre, cliente))


def start():
    global con_man
    con_man = ConnectionManager()

    con_man.beginAcceptingConnections(lambda client : con_man.pedir_respuesta(client, "Escriba su nombre:", __establecer_jugador))

    global jugadores

    con_man.wait_until(lambda : len(jugadores) >= N_JUGADORES)

    print("listos para empezar")