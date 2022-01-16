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


Interfaz.mostrarMensaje("Elige CONECTARSE o CREAR SALA.")


Interfaz.espera_eleccion(["CONECTARSE", "CREAR SALA"], [conectarse, crear_sala])()