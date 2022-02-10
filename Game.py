import sys
from time import sleep
import GameScripts.Interfaz as Interfaz

import GameScripts.Player as Player

import GameScripts.GameManager as GameManager

import threading

end: bool = False

def end_exec():
    global end
    end = True

def conectarse():

    Player.start()


def crear_sala():

    thread = threading.Thread(target=GameManager.start)
    thread.daemon = True
    thread.start()

    Player.start()

thread1 = threading.Thread(target=Interfaz.main_loop)
thread1.daemon = True
thread1.start()

sleep(0.1)
Interfaz.events.on_close += end_exec
Interfaz.events.on_create += crear_sala
Interfaz.events.on_connect += conectarse

Interfaz.connection_screen()

while not end:
    sleep(0.1)

print("dfskjdfsjk")
sys.exit()