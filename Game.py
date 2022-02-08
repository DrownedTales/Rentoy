from time import sleep
import GameScripts.Interfaz as Interfaz

import GameScripts.Player as Player

import GameScripts.GameManager as GameManager

import threading


def conectarse():

    Player.start()


def crear_sala():

    thread = threading.Thread(target=GameManager.start)

    thread.start()

    Player.start()

thread1 = threading.Thread(target=Interfaz.main_loop)
thread1.start()

sleep(0.1)

Interfaz.connection_screen((conectarse, crear_sala))

#Interfaz.mostrarMensaje("Elige CONECTARSE o CREAR SALA.")
#Interfaz.espera_eleccion(["CONECTARSE", "CREAR SALA"], [conectarse, crear_sala])()
while True:
    sleep(0.1)