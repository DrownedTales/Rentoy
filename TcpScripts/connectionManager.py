import time
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), os.path.pardir)))
from TcpScripts.server import Server
from TcpScripts.ClaseCliente import Cliente

class ConnectionManager:
    server: Server = None

    on_client_connect_func = None

    peticiones = dict()


    def wait_until(self, predicate, period=0.25, *args, **kwargs):
        while True:
            if predicate(*args, **kwargs):
                return
            time.sleep(period)

    def enviar_mensaje(self, cliente: Cliente, msg):
        self.server.send_message(cliente, msg, "texto")

    def pedir_eleccion(self, cliente: Cliente, texto_peticion, elecciones, funciones):
        self.enviar_mensaje(cliente, texto_peticion)
        self.server.send_message(cliente, (elecciones, funciones), "eleccion")

    def pedir_respuesta(self, cliente: Cliente, texto_peticion, funcion):
        self.peticiones[cliente] = funcion
        self.server.send_message(cliente, texto_peticion, "peticion")


    def on_message_recived(self, msg, type_of_msg: str, client: Cliente):
        if self.peticiones[client] != None:
            func = self.peticiones[client]
            self.peticiones[client] = None
            func(msg, client)

    def on_client_exit(client: Cliente):
        pass

    def on_client_connect(self, client: Cliente):
        self.on_client_connect_func(client)


    def beginAcceptingConnections(self, func):
        self.on_client_connect_func = func
        self.server.beginAcceptingConnections()

    def stopAcceptingConnections(self):
        self.server.stopAcceptingConnections()


    def __init__(self) -> None:
        self.server = Server()

        self.server.events.on_message_recived += self.on_message_recived
        self.server.events.on_client_exit += self.on_client_exit
        self.server.events.on_client_connect += self.on_client_connect
