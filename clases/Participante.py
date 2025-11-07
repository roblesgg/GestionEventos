class Participante:

    #Constructor
    def __init__(self, IdParticipante, nombre):
        

        self.IdParticipante = IdParticipante
        self.nombre = nombre
        
        #lista de preferencias
        self.preferencias = []
        
        #lista de los que no se pueden sentar comn el no me acuerdo como se llamaban
        self.evitados = []
        
        #Para guardar el id de la mesa
        self.mesaAsignada = None

        
    #Metodos

    #Añade a preferencias a otro invitado
    def anadirPreferencia(self, nombreParticipante):
        #Combprueba que no este ya añadido ni sea el mismo
        if nombreParticipante not in self.preferencias and nombreParticipante != self.nombre:
            self.preferencias.append(nombreParticipante)

    #Elimina de preferencias
    def eliminar_preferencia(self, nombreParticipante):
        try:
            # Intenta borrar el nombre de la lista de preferencias
            self.preferencias.remove(nombreParticipante)
        except ValueError:
            print("Error")


    #Añade a evitar"
    def anadirEvitado(self, nombreParticipante):
        #Combprueba que no este ya añadido ni sea el mismo
        if nombreParticipante not in self.evitados and nombreParticipante != self.nombre:
            self.evitados.append(nombreParticipante)

    #Elimina de evitados
    def eliminar_evitado(self, nombre_participante):
        try:
            self.evitados.remove(nombre_participante)
        except ValueError:
            print("Error")
            