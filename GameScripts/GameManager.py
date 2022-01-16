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
    jugador_creado = Jugador(nombre, cliente)
    jugadores.append(jugador_creado)
    con_man.enviar_mensaje(cliente, ("set jugador", jugador_creado))

def boca_arriba(jugador):
    con_man.enviar_mensaje(__get_clientes_de(jugadores), Carta(a, b))

def boca_abajo():
    pass

def envio():
    pass
    

def comienzo_ronda(n_rondas):

    con_man.enviar_mensaje(__get_clientes_de(jugadores), ("resetear ronda", n_rondas))

    mazo = crear_mazo()

    vira: Carta = sacar_carta_aleatoria(mazo)

    con_man.enviar_mensaje(__get_clientes_de(jugadores), vira)

    for i in range(len(jugadores)):
        for e in range(n_rondas):
            carta = sacar_carta_aleatoria(mazo)
            con_man.enviar_mensaje(jugadores[i].cliente, carta)

    '''
    Tenemos 3 opciones:
        -   Echar la carta boca arriba
        -   Echar la carta boca abajo
        -   Enviar (Apostar)

    Todo jugador que empiece la ronda deberá a la fuerza echar la carta boca arriba (Esto se debe a que no existe la 2ª carta que manda).
    '''
    ### HACER COSAS ###

    con_man.pedir_eleccion(__get_clientes_de(jugadores[0]), "Elija su opción (BOCA ARRIBA, ENVIO)", ("BOCA ARRIBA", "ENVIO"), (boca_arriba, envio))



def comienzo_super_ronda():
    for i in range(3):
        comienzo_ronda(i)

def comienzo_sprint_final():
    comienzo_ronda(3)

def comienzo_quiero():
    comienzo_ronda(3)
    ### ESTO ES MAS COMPLICAO. HAY QUE PREGUNTARLE AL EQUIPO CON 29 PUNTOS SI QUISIERA JUGAR LA RONDA O NO ###

def turnos(parametro):
    pass

def game_loop():
    while True:

        puntuacion1 = 0
        puntuacion2 = 0

        while puntuacion1 < 21 or puntuacion2 < 21:
            comienzo_super_ronda()
        while puntuacion1 < 29 or puntuacion2 < 29:
            comienzo_sprint_final()
        while puntuacion1 < 30 or puntuacion2 < 30:
            comienzo_quiero()


def start():
    global con_man
    con_man = ConnectionManager()

    con_man.beginAcceptingConnections(lambda client : con_man.pedir_respuesta(client, "Escriba su nombre:", __establecer_jugador))

    global jugadores

    con_man.wait_until(lambda : len(jugadores) >= N_JUGADORES)

    con_man.stopAcceptingConnections()

    print("Listos para empezar...")

    game_loop()