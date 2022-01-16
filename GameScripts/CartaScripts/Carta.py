
palos = ["Oros", "Copas", "Espadas", "Bastos"]
valores = ["As", "2", "3", "4", "5", "6", "7", "Sota", "Caballo", "Rey"]

class Carta:

    palo : str
    valor : str

    def to_string(self):
        return self.valor + " de " + self.palo

    def __init__(self, a, b):

        if a not in valores:
            raise Exception("Este valor no es válido")
        if b not in palos:
            raise Exception("Este palo no es válido")

        self.valor = a
        self.palo = b