import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), os.path.pardir)))
from TcpScripts.ClaseCliente import Cliente

class Jugador:
    name : str
    cliente : Cliente

    
