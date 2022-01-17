import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), os.path.pardir)))
from TcpScripts.connectionManager import ConnectionManager

from GameScripts.ClasePlayer import Jugador
from GameScripts.CartaScripts.Mazo import *
from GameScripts.Player import *

N_JUGADORES = 1

jugadores = dict()

con_man : ConnectionManager = None

def __get_clientes_de(jugadores):
    clientes = []
    for nombre in jugadores.keys():
        clientes.append(jugadores[nombre].cliente)
    return clientes

def __establecer_jugador(nombre, cliente):
    print("nuevo jugador: " + nombre)
    jugadores[nombre] = Jugador(nombre, cliente)
    con_man.enviar_mensaje(cliente, ("set jugador", nombre))

def colocarla_boca_arriba(mano):
    pass

def eleccion_carta(mano):
    #################################
    #con_man.pedir_eleccion(jugadores["ale"].cliente, "Elija su carta " + str(mano),tuple(mano), (lambda : colocarla_boca_arriba(mano)))
    pass

def boca_arriba(nombre_jugador, manos):
    mano = manos[nombre_jugador]
    eleccion_carta(mano)

def boca_abajo(nombre_jugador):
    pass

def envio(nombre_jugador):
    pass
    

def comienzo_ronda(n_rondas):

    con_man.enviar_mensaje(__get_clientes_de(jugadores), ("resetear ronda", n_rondas + 1))

    mazo = crear_mazo()
    manos = dict()

    vira: Carta = sacar_carta_aleatoria(mazo)

    con_man.enviar_mensaje(__get_clientes_de(jugadores), vira)

    for i in jugadores.keys():
        for e in range(n_rondas):
            carta = sacar_carta_aleatoria(mazo)
            con_man.enviar_mensaje(jugadores[i].cliente, carta)
            clave = jugadores[i].nombre
            if clave not in manos:
                manos[clave] = [carta]
            else:
                manos[clave].append(carta)
            
    '''
    Tenemos 3 opciones:
        -   Echar la carta boca arriba
        -   Echar la carta boca abajo
        -   Enviar (Apostar)

    Todo jugador que empiece la ronda deberá a la fuerza echar la carta boca arriba (Esto se debe a que no existe la 2ª carta que manda).
    '''
    ### HACER COSAS ###

    con_man.pedir_eleccion(jugadores["ale"].cliente, "Elija su opción (BOCA ARRIBA, ENVIO)",\
        ("BOCA ARRIBA", "ENVIO"), (lambda x : boca_arriba(x, manos), envio))


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

    
    '''
    #esperar_eleccion para el codigo hasta que el cliente responda y devuelve la opcion correspondiente a las opciones
    print(con_man.esperar_eleccion(jugadores["ale"].cliente, "elige la mejor patata", ("de sanlucar", "no de sanlucar"), ("sipi", "este es tonto")))

    #esperar_respuesta para el codigo hasta que el cliente responda y devuelve su respuesta
    print(con_man.esperar_respuesta(jugadores["ale"].cliente, "dime algo guapo"))

    #enviar_mensaje envia un mensaje al cliente
    con_man.enviar_mensaje(jugadores["ale"].cliente, "tu ere tonto")

    #pedir_eleccion no para el codigo. Cuando el cliente responda se llama a la funcion correspondiente a esa respuesta pasandole el nombre del jugador
    con_man.pedir_eleccion(jugadores["ale"].cliente, "elige muerte o mas muerte", ("muerte", "tus muertos"),\
        (lambda x : print(x + " dice muerte"), lambda x : print(x + " tus muertos pisaos")))
    
    #pedir_respuesta no para el codigo. Cuando el cliente responda se llama a la funcion pasandole la respuesta y el nombre del jugador
    con_man.pedir_respuesta(jugadores["ale"].cliente, "dime puto", lambda x, c : print(x[1] + " dice que " + str(x[0])))


    #ahora arregla lo de ayer que estaba dormido y no recuerdo ni lo que hicimos

    '''


    #game_loop()