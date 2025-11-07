class Evento:

    
    def __init__(self, IdEvento, nombre, fecha, ubicacion, organizador, numMesas):
        
        #Atributos
        self.IdEvento = IdEvento
        self.nombre = nombre
        self.fecha = fecha
        self.ubicacion = ubicacion
        self.organizador = organizador
        self.numMesas = numMesas
        
        #Lista para participantes
        self.participantes = []
        
        #Lista para mesas
        self.mesas = [] 

    #Metodos

    def anadirparticipante(self, participante):
        #Comprueba que no este ya
        if participante not in self.participantes:
            self.participantes.append(participante)

    def eliminarParticipante(self, participante):
            try:
                self.participantes.remove(participante)
            except:
                 print("Error al borrar")
        
