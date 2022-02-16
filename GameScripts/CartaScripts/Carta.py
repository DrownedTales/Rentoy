
palos = ["Oro", "Copa", "Espada", "Basto"]
valores = ["2", "3", "4", "5", "6", "7", "As", "Sota", "Caballo", "Rey"]

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

    def __eq__(self, __o: object) -> bool:
        if type(__o) == Carta:
            if __o.palo == self.palo and __o.valor == self.valor:
                return True
        return False

    def mayorq(self, vira, secvira, otra, orden, orden_otra) -> bool:
        res = False

        lista = list(enumerate(valores))

        if self.palo == otra.palo:
            if self.palo == vira.palo:
                lista[0][0] = 100
            for orden,value in lista:
                if self.valor == value:
                    orden_pro = orden
                if otra.valor == value:
                    orden_otra = orden
                
            if orden_pro > orden_otra:
                res = True
            
        else:
            if self.palo == vira.palo and otra.palo != vira.palo:
                res = True
            elif self.palo == secvira.palo and (otra.palo != vira.palo and otra.palo != secvira.palo):
                res = True
            elif (self.palo != secvira.palo and self.palo != vira.palo) and (otra.palo != vira.palo and otra.palo != secvira.palo):
                if orden < orden_otra:
                    res = True
        
        return res