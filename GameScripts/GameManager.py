import os
import sys
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), os.path.pardir)))
from TcpScripts.connectionManager import ConnectionManager

from GameScripts.ClasePlayer import Jugador
from GameScripts.CartaScripts.Mazo import *
from GameScripts.Player import *

N_JUGADORES = 4
N_EQUIPOS = 2
TIME_BETWEEN_CARDS = 0.8

jugadores = dict()

con_man : ConnectionManager = None

dealer_index = 0

cartas_juego = dict()

equipos = dict()

puntuaciones = dict()

orden_jugadores = []

puntos = 1

vira: Carta = None
sec_vira : Carta = None

def __get_clientes_de(jugadores):
    clientes = []
    for nombre in jugadores.keys():
        clientes.append(jugadores[nombre].cliente)
    return clientes

#hacer que el nombre tenga que ser al menos 3 letras
def __establecer_jugador(nombre, cliente):
    print("llama", nombre, cliente)
    if nombre in jugadores.keys():
        con_man.enviar_mensaje(cliente, ("error", "ese nombre ya esta en uso", Interfaz.connection_screen))
        con_man.server.close_connection(cliente)
        return
    jugadores[nombre] = Jugador(nombre, cliente)
    con_man.enviar_mensaje(cliente, ("set jugador", nombre))
    con_man.enviar_mensaje(__get_clientes_de(jugadores), ("update waiting players", tuple(jugadores.keys()), N_JUGADORES))
    print("jugadores", jugadores.keys())

def establecer_equipos(nombre_jugador, nombre_equipo):
    print(nombre_equipo, nombre_jugador)
    if nombre_equipo in equipos.keys():
        if len(equipos[nombre_equipo]) >= N_JUGADORES/N_EQUIPOS:
                con_man.enviar_mensaje(jugadores[nombre_jugador].cliente, ("error", "ese equipo ya está lleno", None))
                pedir_equipos(jugadores[nombre_jugador].cliente)
                return
        equipos[nombre_equipo].append(nombre_jugador)
    else:
        equipos[nombre_equipo] = [nombre_jugador]
        puntuaciones[nombre_equipo] = 0
    con_man.enviar_mensaje([jugadores[i].cliente for a in equipos.values() for i in a], ("update waiting teams", equipos))

def __get_order_carta(carta):
    for i in cartas_juego.keys():
        if cartas_juego[i] == carta:
            jugador = i 
            break
    orden = enumerate(orden_jugadores)
    for o,v in orden:
        if v == jugador:
            orden_jugador = o

    orden_jugador += len(orden_jugadores)
    orden_jugador -= dealer_index
    orden_jugador = orden_jugador%len(orden_jugadores)

    return orden_jugador

def sumar_puntos(puntos, jugador):
    for i in equipos.keys():
        if jugador in equipos[i]:
            puntuaciones[i] += puntos
            break

def ganar_puntos(puntos):
    carta_max : Carta = None
    for carta in cartas_juego.values():
        contador = 0
        for otra in cartas_juego.values():
            if otra != carta:
                if not carta.mayorq(vira, sec_vira, otra, __get_order_carta(carta), __get_order_carta(otra)):
                    break
                else:
                    contador += 1
        if contador == (len(cartas_juego)-1):
            carta_max = carta
            break
    jugador = None
    for i in cartas_juego.keys():
        if cartas_juego[i] == carta_max:
            jugador = i 
            break
    sumar_puntos(puntos, jugador)

def eleccion_carta(nombre_jugador, mano):
    return con_man.esperar_eleccion(jugadores[nombre_jugador].cliente, "CARD", tuple(mano), tuple(mano))

def boca_arriba(nombre_jugador, mano):
    global cartas_juego

    carta = eleccion_carta(nombre_jugador, mano)
    mano.remove(carta)
    con_man.enviar_mensaje(__get_clientes_de(jugadores), ("jugar carta", "up", nombre_jugador, carta))
    cartas_juego[nombre_jugador] = carta
    return carta

def boca_abajo(nombre_jugador, mano):
    global cartas_juego

    carta = eleccion_carta(nombre_jugador, mano)
    mano.remove(carta)
    con_man.enviar_mensaje(__get_clientes_de(jugadores), ("jugar carta", "down", nombre_jugador, carta))
    cartas_juego[nombre_jugador] = carta
    return carta

def envio(nombre_jugador, otro_jugador, puntos):
    if puntos == 1:
        new_puntos = puntos + 2
    elif puntos >= 3:
        new_puntos = puntos + 3
    respuesta = con_man.pedir_eleccion(jugadores[otro_jugador].cliente, "ENVIO", ("acepto", "no acepto", "subo: "+str(new_puntos)), ("acepto","no acepto","subo"))
    if respuesta == "acepto":
        return new_puntos, True
    elif respuesta == "no acepto":
        return puntos, False, nombre_jugador
    elif respuesta == "subo":
        return envio(otro_jugador, nombre_jugador, new_puntos)
    

def comienzo_ronda(n_rondas):

    con_man.enviar_mensaje(__get_clientes_de(jugadores), ("start game", orden_jugadores))

    sleep(TIME_BETWEEN_CARDS)

    mazo = crear_mazo()
    manos = dict()

    global dealer_index
    dealer_index = (dealer_index + 1) % N_JUGADORES

    global cartas_juego
    cartas_juego = dict()

    dealer = orden_jugadores[dealer_index]

    global vira
    vira = sacar_carta_aleatoria(mazo)

    global sec_vira
    sec_vira = None

    global puntos
    puntos = 1

    con_man.enviar_mensaje(__get_clientes_de(jugadores), ("set vira", vira))
    sleep(TIME_BETWEEN_CARDS)

    for i in jugadores.keys():
        for e in range(n_rondas):
            carta = sacar_carta_aleatoria(mazo)
            print("sending to", i)
            con_man.enviar_mensaje(jugadores[i].cliente, ("add player card", carta))
            con_man.enviar_mensaje(__get_clientes_de(jugadores), ("add card", i))
            clave = jugadores[i].name
            if clave not in manos:
                manos[clave] = [carta]
            else:
                manos[clave].append(carta)
            sleep(TIME_BETWEEN_CARDS)
            
    '''
    Tenemos 3 opciones:
        -   Echar la carta boca arriba
        -   Echar la carta boca abajo
        -   Enviar (Apostar)

    Todo jugador que empiece la ronda deberá a la fuerza echar la carta boca arriba (Esto se debe a que no existe la 2ª carta que manda).
    '''
    print("le toca a ", dealer)
    x = con_man.esperar_eleccion(jugadores[dealer].cliente, "ACTION", ("Echar boca arriba", "Envio"), ("a", "b"))
    print("recived action!")
    if x == "a":
        carta = boca_arriba(dealer, manos[dealer])
        if sec_vira == None:
            sec_vira = carta
        con_man.enviar_mensaje(__get_clientes_de(jugadores), ("set sec vira", sec_vira))

    elif x == "b":
        res = envio(dealer, orden_jugadores[(dealer_index + 1) % N_JUGADORES], puntos)
        puntos = res[0]
        if res[1] == False:
            sumar_puntos(puntos, res[2])
            return

    #sleep(100000)
    sleep(TIME_BETWEEN_CARDS)

    for e in range(3):
        jugador_q_le_toca = orden_jugadores[(dealer_index+1+e) % N_JUGADORES]
        print("le toca a ", jugador_q_le_toca)
        x = con_man.esperar_eleccion(jugadores[jugador_q_le_toca].cliente, "ACTION", ("Echar boca arriba", "Echar boca abajo", "Envio"), ("a", "b", "c"))
        print("recived action!")
        if x == "a":
            boca_arriba(jugador_q_le_toca, manos[jugador_q_le_toca])
        elif x == "b":
            boca_abajo(jugador_q_le_toca, manos[jugador_q_le_toca])
        elif x == "c":
            res = envio(jugador_q_le_toca, orden_jugadores[(dealer_index + e + 1) % N_JUGADORES], puntos)
            puntos = res[0]
            if res[1] == False:
                sumar_puntos(puntos, res[2])
                return
        sleep(TIME_BETWEEN_CARDS)

    sleep(5)

    ganar_puntos(puntos)

def comienzo_super_ronda():
    for i in range(1,4):
        comienzo_ronda(i)

def comienzo_sprint_final():
    comienzo_ronda(3)

def comienzo_quiero():
    comienzo_ronda(3)
    # ESTO ES MAS COMPLICAO. HAY QUE PREGUNTARLE AL EQUIPO CON 29 PUNTOS SI QUISIERA JUGAR LA RONDA O NO

def game_loop():
    while True:
        puntuacion1 = puntuaciones[list(equipos.keys())[0]]
        puntuacion2 = puntuaciones[list(equipos.keys())[1]]

        while puntuacion1 < 21 or puntuacion2 < 21:
            comienzo_super_ronda()
        while puntuacion1 < 29 or puntuacion2 < 29:
            comienzo_sprint_final()
        while puntuacion1 < 30 or puntuacion2 < 30:
            comienzo_quiero()

def pedir_equipos(clientes):
    #nombre_equipos = [str(i) for i in range(int(len(jugadores)/2))]
    nombre_equipos = [i for i in range(N_EQUIPOS)]
    respuestas = [(lambda x, i=i: establecer_equipos(x, nombre_equipos[i])) for i in range(len(nombre_equipos))]

    con_man.pedir_eleccion(clientes, "Elige equipo", tuple(nombre_equipos), tuple(respuestas))


def start():
    global con_man
    con_man = ConnectionManager()
    
    con_man.beginAcceptingConnections(lambda client : con_man.pedir_respuesta(client, "Escriba su nombre:", __establecer_jugador))

    global jugadores

    con_man.wait_until(lambda : len(jugadores) >= N_JUGADORES)

    con_man.stopAcceptingConnections()

    pedir_equipos(__get_clientes_de(jugadores))

    con_man.wait_until(lambda : sum([len(i) for i in equipos.values()]) == len(jugadores))
    

    global orden_jugadores
    for e in range(max([len(i) for i in equipos.values()])):
        for i in equipos.values():
            try:
                orden_jugadores.append(i[e])
            except:
                pass

    print("Listos para empezar...")

    game_loop()




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