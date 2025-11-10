# clases/GestorDatos.py
import json
import os 
from .Evento import Evento
from .Participante import Participante
from .Mesa import Mesa




class GestorDatos:


    #Constructor
    def __init__(self, nombreArchivo):
        #Declara el archivo para guardar la ruta
        self.rutaArchivo = nombreArchivo
        

    #Guardar los evemtos
    def guardarEventos(self, listaDeEventos):
        #Lista de eventos
        listaParaGuardar = []
        
        # Recorre los eventos de la lista
        for evento in listaDeEventos:
            
            #Traduce el objeto evento a un diccionario simple.
            eventoDict = {
                "IdEvento": evento.IdEvento,
                "nombre": evento.nombre,
                "fecha": evento.fecha,
                "ubicacion": evento.ubicacion,
                "organizador": evento.organizador,
                "numMesas": evento.numMesas,
                "participantes": [], #falta que la llenemossssssssssssssssssssssssssssss
                "mesas": []         #falta que la llenemossssssssssssssssssssssssssssss
            }
            
            #traduce los participantes
            for participante in evento.participantes:
                participanteDict = {
                    "IdParticipante": participante.id_participante, 
                    "nombre": participante.nombre,
                    "preferencias": participante.preferencias,
                    "evitados": participante.evitados,
                    "mesaAsignada": participante.mesa_asignada
                }
                # añade el diccionario de participantes a el de eventos
                eventoDict["participantes"].append(participanteDict)
            
            #traduce la mesa
            for mesa in evento.mesas:
                mesaDict = {
                    "id_mesa": mesa.id_mesa,
                    "numero": mesa.numero,
                    "capacidad": mesa.capacidad,
                    #esto son los ides de los participntes en la mesa
                    "participantes_ids": [p.id_participante for p in mesa.participantes]
                }
                # añade el diccionario de las mesas al del evento
                eventoDict["mesas"].append(mesaDict)
            
            #añade todo a la lista final
            listaParaGuardar.append(eventoDict)

        #escribe la lista final de diccionarios en el archivo JSON
        try:
            #w de write
            #encoding=utf-8 guarda tildes y caracteres especiales
            with open(self.rutaArchivo, 'w', encoding='utf-8') as f:
                # json.dump(QUÉ_GUARDAR, DÓNDE_GUARDARLO, ...)
                json.dump(listaParaGuardar, f, indent=4, ensure_ascii=False)
                
        except Exception as e:
            # Si algo sale mal (ej: permisos de archivo), lo mostramos.
            print(f"Error al guardar eventos en {self.rutaArchivo}: {e}")


    #cargar los eventos
    def cargarEventos(self):
        
        # Si el archivo de guardado no existe, devuelve una lista vacía.
        if not os.path.exists(self.rutaArchivo):
            return []

        # Intentamos leer el archivo.
        try:
            #r de read
            with open(self.rutaArchivo, 'r', encoding='utf-8') as f:
                # json.load(DE_DÓNDE_LEER) lee el archivo y lo convierte en lista de diccionarios.
                listaLeida = json.load(f)
            
            listaDeEventos = []
            
            # recorre cada diccionario de evento que leímos del JSON.
            for eventoDict in listaLeida:
                
                #Crea evento
                nuevoEvento = Evento(
                    eventoDict['IdEvento'],
                    eventoDict['nombre'],
                    eventoDict['fecha'],
                    eventoDict['ubicacion'],
                    eventoDict['organizador'],
                    eventoDict['numMesas']
                )
                
                participantes_map = {}
                
                # 2. Reconstruir los objetos "Participante" del evento.
                for participanteDict in eventoDict['participantes']:
                    nuevoParticipante = Participante(
                        participanteDict['IdParticipante'],
                        participanteDict['nombre']
                    )
                    # Re-asignamos sus listas de preferencias/evitados y su mesa.
                    nuevoParticipante.preferencias = participanteDict['preferencias']
                    nuevoParticipante.evitados = participanteDict['evitados']
                    nuevoParticipante.mesaAsignada = participanteDict['mesaAsignada']
                    
                    # Añadimos el objeto Participante al objeto Evento.
                    nuevoEvento.anadirparticipante(nuevoParticipante)
                    
                    # --- Lógica Clave ---
                    # Guardamos el objeto en nuestro mapa para encontrarlo luego.
                    participantes_map[nuevoParticipante.id_participante] = nuevoParticipante
                
                nuevoEvento.mesas = []
                
                # Usamos .get("mesas", []) por si el JSON es antiguo y no tiene "mesas".
                for mesaDict in eventoDict.get("mesas", []):
                    # Creamos el objeto "Mesa"
                    nuevaMesa = Mesa(
                        mesaDict['id_mesa'],
                        mesaDict['numero'],
                        mesaDict['capacidad']
                    )
                    
                    # --- Lógica Clave de Re-conexión ---
                    # Ahora leemos la lista de IDs de participantes que guardamos.
                    for participante_id in mesaDict['participantes_ids']:
                        # Buscamos el ID en nuestro mapa.
                        if participante_id in participantes_map:
                            # ¡Encontrado! Obtenemos el OBJETO participante.
                            participante_obj = participantes_map[participante_id]
                            
                            # Y añadimos el OBJETO participante a la lista de la mesa.
                            nuevaMesa.anadirParticipante(participante_obj)
                    
                    # Añadimos la mesa (ya con sus participantes) al evento.
                    nuevoEvento.mesas.append(nuevaMesa)

                # 4. Añadimos el Evento (ya con sus participantes y mesas) a la lista final.
                listaDeEventos.append(nuevoEvento)
                    
            # Devolvemos la lista de objetos Evento completa.
            return listaDeEventos
            
        except Exception as e:
            # Si algo falla (ej: JSON corrupto), lo mostramos y devolvemos lista vacía.
            print(f"Error al cargar eventos desde {self.rutaArchivo}: {e}")
            return []