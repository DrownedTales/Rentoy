import socket

class Cliente:
    ip: str
    socket: socket.socket

    def __init__(self, ip, socket) -> None:
        self.ip = ip
        self.socket = socket