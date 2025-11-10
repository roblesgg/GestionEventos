import json
import os 

# Importamos los moldes para poder reconstruir los objetos
from .Evento import Evento
from .Participante import Participante
from controllers.ControllerBorrarEvento import Ui_DialogoBorrarEvento
from controllers.ControllerCrearEvento2 import Ui_DialogoParticipantes
from controllers.ControllerAsignarMesasManual import Ui_Form as Ui_AsignarManualForm

#Esta clase su unico trabajo es guardar y cargar la lista de eventos en json
class GestorDatos:

    #constructor
    def __init__(self, nombreArchivo):
        self.rutaArchivo = nombreArchivo
        

    
#metodoss
    #guarda eventos
    def guardarEventos(self, listaDeEventos):
        #Recibe una lista de Eventos y la guarda en el JSON.
        
        #lista para los eventos
        listaParaGuardar = []
        
        #Recorre todos los evemtos
        for evento in listaDeEventos:
            
            # traduce el objeto Evento a un diccionario simple
            eventoDict = {
                "IdEvento": evento.IdEvento,
                "nombre": evento.nombre,
                "fecha": evento.fecha,
                "ubicacion": evento.ubicacion,
                "organizador": evento.organizador,
                "numMesas": evento.numMesas,
                "participantes": [], # Lista vacía por ahora
                "mesas": [] # Lista vacía por ahora
            }
            
            #traduce la lista de participantes de este evento
            for p_obj in evento.participantes:
                p_dict = {
                    "IdParticipante": p_obj.IdParticipante,
                    "nombre": p_obj.nombre,
                    "preferencias": p_obj.preferencias,
                    "evitados": p_obj.evitados,
                    "mesaAsignada": p_obj.mesaAsignada
                }
                # añade el diccionario del participante al diccionario del evento
                eventoDict["participantes"].append(p_dict)
            
            #añade el diccionario del evento a nuestra lista final
            listaParaGuardar.append(eventoDict)

        #Guarda todo en el json
        try:
            #la w es de write
            with open(self.rutaArchivo, 'w', encoding='utf-8') as f:
# json.dump(el nombre del archivo,donde se gurda,4 espacios para quelo podamos leer,esto cambia los caracteres raros a ascii)
                json.dump(listaParaGuardar, f, indent=4, ensure_ascii=False)
        except Exception:
            print("Error")


    #cargar el json
    def cargarEventos(self):
        #Lee el archivo json y devuelve una lista de objetosde Evento.
        if not os.path.exists(self.rutaArchivo):
            return []#esto es para que no haga nada

        #la lee
        try:
            #r de read
            with open(self.rutaArchivo, 'r', encoding='utf-8') as f:
                listaLeida = json.load(f)
            
            #hace los objetos del json
            listaDeEventos = []
            
            for eventoDict in listaLeida:
                #crea evento
                nuevoEvento = Evento(
                    eventoDict['IdEvento'],
                    eventoDict['nombre'],
                    eventoDict['fecha'],
                    eventoDict['ubicacion'],
                    eventoDict['organizador'],
                    eventoDict['numMesas']
                )
                
                #crea participantes
                for p_dict in eventoDict['participantes']:
                    nuevoParticipante = Participante(
                        p_dict['IdParticipante'],
                        p_dict['nombre']
                    )
                    #escribe los participantes
                    nuevoParticipante.preferencias = p_dict['preferencias']
                    nuevoParticipante.evitados = p_dict['evitados']
                    nuevoParticipante.mesaAsignada = p_dict['mesaAsignada']
                    
                    #a´ñade al evento
                    nuevoEvento.anadirparticipante(nuevoParticipante)
                
                #añade el evento a la lista
                listaDeEventos.append(nuevoEvento)
                    
            return listaDeEventos
            
        except Exception:
            print("Error")
            return []# no hace nada esto