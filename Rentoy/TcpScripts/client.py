import socket
import pickle
import _thread

HEADERSIZE = 10

ip = '217.216.250.126'
puerto = 1243

class Mensaje:
    emisor = ""
    djskf = 0
    dsjkkjdfskjdsf = 0
    mensajeEnSi = ""

    def __init__(self, e, a, b, m):
        self.emisor = e
        self.djskf = a
        self.dsjkkjdfskjdsf = b
        self.mensajeEnSi = m

a = pickle.dumps(Mensaje("Ale", 145, 13, "hola buenos dias esto es una prueba Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."))
print(a)
print(len(a))


def recibirChat(serversocket):
    while True:
        msg = serversocket.recv(1024)
        chat = pickle.loads(msg)
        print(chat.emisor + " : " + chat.mensajeEnSi)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((ip, puerto))

_thread.start_new_thread(recibirChat, (s, ))

while True:
    a = input("")
    s.send(pickle.dumps(Mensaje("Ale", a)))

'''
while True:
    full_msg = b''
    new_msg = True
    while True:
        msg = s.recv(16)
        if new_msg:
            print("new msg len:",msg[:HEADERSIZE])
            msglen = int(msg[:HEADERSIZE])
            new_msg = False

        print(f"full message length: {msglen}")

        full_msg += msg

        print(len(full_msg))

        if len(full_msg)-HEADERSIZE == msglen:
            print("full msg recvd")
            print(full_msg[HEADERSIZE:])
            print(pickle.loads(full_msg[HEADERSIZE:]))
            new_msg = True
            full_msg = b""
'''