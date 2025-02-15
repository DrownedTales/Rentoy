import socket
import dill as pickle
#import pickle
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

    clientes = []#: list[Cliente]
    our_socket: socket.socket

    accepting: bool = False

    events = Events()

    def beginAcceptingConnections(self):
        self.accepting = True

    def stopAcceptingConnections(self):
        self.accepting = False

    def close_connection(self, client: Cliente):
        print("closed", client.socket)
        client.socket.close()
        self.clientes.remove(client)

    def send_message(self, client: Cliente, msg, type_of_msg):
        if type_of_msg not in self.types_of_msgs:
            raise Exception("type of message not valid")

        content = pickle.dumps(msg)

        msg_lengt = str(len(content))

        header = type_of_msg.ljust(10) + ","+ msg_lengt.ljust(9)

        packet = header.encode("utf-8") + content

        client.socket.send(packet)

    def __listen_to_client(self, client: Cliente):
        while True:

            client_socket = client.socket

            try:
                packet = client_socket.recv(self.packet_size)
            except:
                if client in self.clientes: #se desconecto el
                    self.events.onClientExit(client)
                break

            if len(packet) <= 0:
                continue
            
            header: str = packet[:self.header_size].decode("utf-8")
            type_of_msg = header.split(',')[0].strip()
            msg_length = int(header.split(',')[1].strip())

            if (msg_length > self.packet_size):
                raise Exception("datos demasiado largos. Esto habria que arreglarlo")
            
            msg = pickle.loads(packet[self.header_size:])
            
            self.events.on_message_recived(msg, type_of_msg, client)


    def __accept_loop(self):
        while True:
            if self.accepting == False:
                time.sleep(0.01)
                continue

            clientsocket, address = self.our_socket.accept()

            if self.accepting:
                client = Cliente(address, clientsocket)
                self.clientes.append(client)
                self.events.on_client_connect(client);

                thread = threading.Thread(target=self.__listen_to_client, args=(client, ))
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
                    self.types_of_msgs.append(string.strip())

        #socket init
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.ip, self.puerto))
        s.listen(self.listen_number)

        self.our_socket = s
        print("server socket initialized, ip: " + self.ip + " port: " + str(self.puerto))

        thread = threading.Thread(target=self.__accept_loop)
        thread.start()
