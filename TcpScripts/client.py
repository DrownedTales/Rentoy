import socket
import pickle
import threading
import time
import os
from events import Events


class Client:
    #main variables
    server_ip: str
    server_port: int
    packet_size: int
    header_size: int
    types_of_msgs = []

    my_socket: socket.socket

    events = Events()

    def close_connection(self):
        self.my_socket.close()

    def send_message(self, msg, type_of_msg):
        if type_of_msg not in self.types_of_msgs:
            raise Exception("type of message not valid")

        msg_lengt = str(len(msg))

        header = type_of_msg.ljust(self.header_size / 2) + msg_lengt.ljust(self.header_size / 2)

        packet = bytes(header, "utf-8") + msg

        self.my_socket.send(pickle.dumps(packet))


    def __listen_to_server(self):
        while True:
            if self.listening == False:
                time.sleep(0.01) #para no hacer un bucle infinito sin descanso
                continue

            try:
                packet = self.my_socket.recv(self.packet_size)
            except:
                self.events.on_server_close()
                break

            if len(packet) <= 0:
                continue
            
            header: str = packet[:self.header_size].decode("utf-8")
            type_of_msg = header.split(',')[0].strip()
            msg_length = int(header.split(',')[1].strip())

            if (msg_length > self.packet_size):
                raise Exception("datos demasiado largos. Esto habria que arreglarlo")
            
            msg = pickle.loads(packet[self.header_size:])
            
            self.events.on_message_recived(msg, type_of_msg)



    def __init__(self) -> None:

        #main variables initialization from variables.txt
        lines = []
        with open(os.path.abspath(os.path.join(os.path.dirname( __file__ ), os.path.pardir, 'variables.txt'))) as f:
            lines = f.readlines()

        for line in lines:
            if (line.startswith("SERVER_IP")):
                self.server_ip = (line.split(':')[1]).rstrip()
            elif (line.startswith("SERVER_PORT")):
                self.server_port = int(line.split(':')[1])
            elif (line.startswith("PACKET_SIZE")):
                self.packet_size = int(line.split(':')[1])
            elif (line.startswith("HEADER_SIZE")):
                self.header_size = int(line.split(':')[1])
            elif (line.startswith("TYPES_OF_MSGS")):
                for string in line.split(':')[1].split(','):
                    self.types_of_msgs.append(string)

        #socket init
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            s.connect((self.server_ip, self.server_port))
        except:
            print("no se pudo establecer la conexion")
            self.close_connection()

        self.my_socket = s
        print("client socket initialized, ip: " + self.server_ip + " port: " + str(self.server_port))

        thread = threading.Thread(target=self.__listen_to_server)
        thread.start()