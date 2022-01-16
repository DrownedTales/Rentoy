from GameScripts.CartaScripts.Carta import *
import random

palos = ["Oro", "Copa", "Espada", "Basto"]
valores = ["As", "2", "3", "4", "5", "6", "7", "Sota", "Caballo", "Rey"]

def crear_mazo():
    mazo = []
    for a in palos:
        for b in valores:
            mazo.append(Carta(b,a))
    return mazo

def sacar_carta_aleatoria(mazo):
    carta = random.choice(mazo)
    mazo.remove(carta)
    return carta
