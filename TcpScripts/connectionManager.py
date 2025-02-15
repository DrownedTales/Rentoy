import time
import os
import sys
from GameScripts.Player import enviar_mensaje

sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), os.path.pardir)))
from TcpScripts.server import Server
from TcpScripts.ClaseCliente import Cliente

class ConnectionManager:
    server: Server = None

    on_client_connect_func = None

    elecciones = []

    peticiones = dict()


    def wait_until(self, predicate, period=0.25, *args, **kwargs):
        while True:
            if predicate(*args, **kwargs):
                return
            time.sleep(period)

    def __accion_para_varios(self, clientes, calling_func):
        if not isinstance(clientes, list):
            if isinstance(clientes, Cliente):
                return False
            else:
                raise Exception("no se ha pasado un cliente valido")
        
        for cliente in clientes:
            calling_func(cliente)

        return True

    def __enviar_un_mensaje(self, cliente, msg):
        self.server.send_message(cliente, msg, "data")

    def __resolver_eleccion(self, msg, cliente):
        if callable(msg[0]):
            msg[0](msg[1])
        else:
            self.elecciones.append(msg[0])

    def __pedir_una_eleccion(self, cliente, texto_peticion, elecciones, funciones):
        self.peticiones[cliente] = self.__resolver_eleccion
        self.server.send_message(cliente, (texto_peticion, elecciones, funciones), "eleccion")

    def __pedir_una_respuesta(self, cliente, texto_peticion, funcion):
        self.peticiones[cliente] = funcion
        self.server.send_message(cliente, texto_peticion, "peticion")


    def enviar_mensaje(self, cliente, msg):
        if self.__accion_para_varios(cliente, lambda c: self.enviar_mensaje(c, msg)):
            return
        self.__enviar_un_mensaje(cliente, msg)

    def pedir_eleccion(self, cliente, texto_peticion, elecciones, funciones):
        if self.__accion_para_varios(cliente, lambda c: self.pedir_eleccion(c, texto_peticion, elecciones, funciones)):
            return
        self.__pedir_una_eleccion(cliente, texto_peticion, elecciones, funciones)

    def pedir_respuesta(self, cliente, texto_peticion, funcion):
        if self.__accion_para_varios(cliente, lambda c: self.pedir_eleccion(c, texto_peticion, funcion)):
            return
        self.__pedir_una_respuesta(cliente, texto_peticion, funcion)

    def esperar_eleccion(self, cliente, texto_peticion, elecciones, respuestas):
        self.pedir_eleccion(cliente, texto_peticion, elecciones, respuestas)
        self.wait_until(lambda : self.peticiones[cliente] == None)
        return self.elecciones.pop(len(self.elecciones) - 1)

    def esperar_respuesta(self, cliente, texto_peticion):
        self.pedir_respuesta(cliente, texto_peticion, lambda m, c: self.elecciones.append(m))
        self.wait_until(lambda : self.peticiones[cliente] == None)
        return self.elecciones.pop(len(self.elecciones) - 1)


    def on_message_recived(self, msg, type_of_msg: str, client: Cliente):
        if self.peticiones[client] != None:
            func = self.peticiones[client]
            self.peticiones[client] = None
            func(msg, client)

    def on_client_exit(client: Cliente):
        pass

    def on_client_connect(self, client: Cliente):
        print("hola", client)
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
