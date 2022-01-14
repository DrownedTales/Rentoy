import socket
import pickle
import threading
import time
import os
from events import Events

from TcpScripts.ClaseCliente import Cliente


class Server:
    #main variables
    ip: str
    puerto: int
    listen_number: int
    packet_size: int
    header_size: int
    types_of_msgs = []

    clientes: list[Cliente]
    our_socket: socket.socket

    accepting: bool = False
    listening: bool = False

    events = Events()

    def beginAcceptingConnections(self):
        self.accepting = True

    def stopAcceptingConnections(self):
        self.accepting = False

    def close_connection(self, client: Cliente):
        self.clientes.remove(client)
        client.socket.close()

    def send_message(self, client: Cliente, msg, type_of_msg):
        if type_of_msg not in self.types_of_msgs:
            raise Exception("type of message not valid")

        msg_lengt = str(len(msg))

        header = type_of_msg.ljust(self.header_size / 2) + msg_lengt.ljust(self.header_size / 2)

        packet = bytes(header, "utf-8") + msg

        client.socket.send(pickle.dumps(packet))

    def send_message_to_all(self, msg):
        for client in self.clientes:
            client.socket.send(pickle.dumps(msg))


    def __listen_to_client(self, client: Cliente):
        while True:
            if self.listening == False:
                time.sleep(0.01) #para no hacer un bucle infinito sin descanso
                continue

            client_socket = client.socket

            try:
                packet = client_socket.recv(self.packet_size)
            except:
                if client in self.clientes: #se desconecto el
                    self.events.onClientExit(client)
                self.close_connection(client)
                break

            if len(packet) <= 0:
                continue
            msg = pickle.loads(packet)
            self.events.on_message_recived(msg, client)


    def __accept_loop(self):
        while True:
            if self.accepting == False:
                time.sleep(0.01)
                continue

            clientsocket, address = self.ourSocket.accept()

            if self.accepting:
                client = Cliente(address, clientsocket)
                self.clientes.append(client)
                self.events.on_client_connect(client);

                thread = threading.Thread(target=self.__listen_to_client, args=(clientsocket, ))
                thread.start()


    def __init__(self) -> None:

        #main variables initialization from variables.txt
        lines = []
        with open(os.path.abspath(os.path.join(os.path.dirname( __file__ ), os.path.pardir, 'variables.txt'))) as f:
            lines = f.readlines()

        for line in lines:
            if (line.startswith("SERVER_IP")):
                self.ip = (line.split(':')[1]).rstrip()
            elif (line.startswith("SERVER_PORT")):
                self.puerto = int(line.split(':')[1])
            elif (line.startswith("LISTEN_NUMBER")):
                self.listen_number = int(line.split(':')[1])
            elif (line.startswith("PACKET_SIZE")):
                self.packet_size = int(line.split(':')[1])
            elif (line.startswith("HEADER_SIZE")):
                self.header_size = int(line.split(':')[1])
            elif (line.startswith("TYPES_OF_MSGS")):
                for string in line.split(':')[1].split(','):
                    self.types_of_msgs.append(string)

        #socket init
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.ip, self.puerto))
        s.listen(self.listen_number)

        self.our_socket = s
        print("server socket initialized, ip: " + self.ip + " port: " + str(self.puerto))

        thread = threading.Thread(target=self.__accept_loop)
        thread.start()
