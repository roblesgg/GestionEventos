class Mesa:


    def __init__(self, id_mesa, numero, capacidad=10):
        
        self.id_mesa = id_mesa
        self.numero = numero
        self.capacidad = capacidad
        
        #lista apara los participantes
        self.participantes = [] 

    def anadirParticipante(self, participante):
        if not self.estaLlena():
            if participante not in self.participantes:
                self.participantes.append(participante)
                return True#hechooo
        return False#no hecho

    def eliminarParticipante(self, participante):
        try:
            self.participantes.remove(participante)
            return True
        except ValueError:
            return False#si hay error

#ver si esta llena
    def estLlena(self):
        return len(self.participantes) >= self.capacidad

    def obtenerNombresParticipantes(self):
        return [p.nombre for p in self.participantes]
