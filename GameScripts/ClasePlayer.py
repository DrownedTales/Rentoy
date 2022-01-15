import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), os.path.pardir)))
from TcpScripts.ClaseCliente import Cliente

class Jugador:
    name : str
    cliente : Cliente

    def __init__(self, name, cliente) -> None:
        self.name = name
        self.cliente = cliente
