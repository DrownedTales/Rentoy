import sys
sys.path.append('GameScripts')
import Interfaz
import Player
import GameManager

def conectarse():
    Player.start()

def crear_sala():
    GameManager.start()
    Player.start()

Interfaz.mostrarMensaje("Elige CONECTARSE o CREAR SALA.")

Interfaz.esperaRespuesta(["CONECTARSE", "CREAR SALA"], [conectarse, crear_sala])()

