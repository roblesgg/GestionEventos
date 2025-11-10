class Evento:

    #Constructor
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
        capacidad_por_mesa = 10
        #se crean las mesas
        for i in range(numMesas):
            # Creamos un ID único para la mesa (ej: "evento_boda_mesa_1")
            id_mesa = f"{self.IdEvento}_mesa_{i+1}"
            nueva_mesa = Mesa(id_mesa=id_mesa, numero=i+1, capacidad=capacidad_por_mesa)
            self.mesas.append(nueva_mesa)
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
        
