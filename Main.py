import sys
import os
import webbrowser
import csv
from PyQt5.QtWidgets import QApplication, QWidget, QStackedWidget, QMessageBox, QTableWidgetItem

import random

# aqui traemos todo lo que necesitamos
# y las cosas que usa el programa

# los diseños de las pantallas
from controllers.CrudEvento import Ui_MainWindow
from controllers.ControllerCrearEvento1 import Ui_Form as Ui_CrearEventoForm
from ortools.sat.python import cp_model 
print("--- OR-TOOLS IMPORTADO CON EXITO ---") 
import random
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from controllers.ControllerAsignarMesas import Ui_Form as Ui_PaginaMesas
from controllers.EditarEvento import Ui_Form as Ui_ActualizarEventoForm
from controllers.ControllerAsignarMesasManual import Ui_Form as Ui_AsignarManual
from controllers.ControllerBorrarEvento import Ui_DialogoBorrarEvento as Ui_Borrar
from controllers.ControllerAsignarMesasAutomatico import Ui_Form as Ui_ResultadosAuto
from controllers.ControllerAsignarMesasExcepciones import Ui_Form as Ui_Excepciones

from controllers.ControllerCrearEvento2 import Ui_DialogoParticipantes

# las plantillas (clases) para eventos, mesas, etc
from clases.GestorDatos import GestorDatos
from clases.Evento import Evento
from clases.Participante import Participante
from clases.Mesa import Mesa


# plantillas para cada pantalla

# ventana principal
class PaginaCrud(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

# ventana de crear evento
class PaginaCrearEvento(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_CrearEventoForm()
        self.ui.setupUi(self)

# ventana de asignar mesas
class PaginaMesas(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_PaginaMesas()
        self.ui.setupUi(self)
        
# ventana de actualizar evento
class PaginaActualizarEvento(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ActualizarEventoForm()
        self.ui.setupUi(self)

# ventana de asignar a mano
class Manual(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_AsignarManual()
        self.ui.setupUi(self)  

# ventana de borrar
class PaginaBorrar(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Borrar()
        self.ui.setupUi(self)

# ventana de gestionar invitados
class PaginaGestionarParticipantes(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_DialogoParticipantes()
        self.ui.setupUi(self)

# ventana de resultados automaticos
class PaginaMesasAutomatico(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ResultadosAuto()
        self.ui.setupUi(self)

# ventana de excepciones (los que no caben)
class PaginaExcepciones(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Excepciones()
        self.ui.setupUi(self)

# la ventana jefa, la que controla todo
class VentanaPrincipal(QStackedWidget):
    def __init__(self):
        super().__init__()
        
        # guarda y lee del archivo eventos.json
        self.gestor_datos = GestorDatos("eventos.json") 
        # aqui guardamos los eventos
        self.lista_eventos = []
        # el evento que estamos tocando ahora
        self.evento_en_edicion_actual = None
        # los invitados que no entran en automatico
        self.lista_excepciones = []

        # variables para saber que estamos haciendo
        self.modo_gestion_participantes = None # 'crear' o 'actualizar' invitado
        self.participante_en_gestion = None # el invitado que estamos editando
        self.mesa_manual_actual_idx = 0     # la mesa que vemos en manual
        self.excepcion_mesa_actual_idx = 0  # la mesa que vemos en excepciones
        self.CSV_EXPORT_PATH = "CSVs_Generados" # la carpeta donde guardamos los csv

        # crea las ventanas
        self.pagina_crud = PaginaCrud()           #0
        self.pagina_crear = PaginaCrearEvento()     #1
        self.pagina_actualizar = PaginaActualizarEvento() #2
        self.pagina_mesas = PaginaMesas()         #3
        self.pagina_manual=Manual()             #4
        self.pagina_borrar=PaginaBorrar()       #5
        self.pagina_participantes = PaginaGestionarParticipantes() #6
        self.pagina_resultados_auto = PaginaMesasAutomatico() #7
        self.pagina_excepciones = PaginaExcepciones() #8
        
        # mete las ventanas en el taco
        self.addWidget(self.pagina_crud)           #0
        self.addWidget(self.pagina_crear)         #1
        self.addWidget(self.pagina_actualizar)    #2
        self.addWidget(self.pagina_mesas)          #3
        self.addWidget(self.pagina_manual)          #4
        self.addWidget(self.pagina_borrar)         #5
        self.addWidget(self.pagina_participantes)  #6
        self.addWidget(self.pagina_resultados_auto) #7
        self.addWidget(self.pagina_excepciones) #8

        # conectamos los botones
        
        # botones de la ventana principal
        self.pagina_crud.ui.CreateEvent_Btn.clicked.connect(self.mostrar_pagina_crear)
        self.pagina_crud.ui.UpdateEvent_Btn.clicked.connect(self.mostrar_pagina_actualizar)
        self.pagina_crud.ui.AssignTables_Btn.clicked.connect(self.mostrar_pagina_mesas)
        self.pagina_crud.ui.DeleteEvent_Btn.clicked.connect(self.mostrar_pagina_borrar)
        
        # boton de asignar automatico
        self.pagina_mesas.ui.AutoAssign_Btn.clicked.connect(self.ejecutar_asignacion_automatica)
        
        # boton para ver quien se quedo fuera
        self.pagina_resultados_auto.ui.ViewExceptions_Btn.clicked.connect(self.mostrar_pagina_excepciones)

        # otros botones
        self.pagina_mesas.ui.ManualAssign_Btn.clicked.connect(self.mostrar_pagina_manual)
        self.pagina_crear.ui.CreateManual_Btn.clicked.connect(self.preparar_evento_para_participantes)
        
        # boton para abrir la carpeta de los csv
        self.pagina_crud.ui.OpenCSVPath_Btn.clicked.connect(self.abrir_carpeta_csvs)
        
        # los botones de subir csv
        self.pagina_crear.ui.UploadCSV_Btn.clicked.connect(self.cargar_participantes_csv)
        self.pagina_actualizar.ui.UploadCSV_Btn.clicked.connect(self.cargar_participantes_csv)

        # boton "crear manual" en la ventana de actualizar
        self.pagina_actualizar.ui.CreateManual_Btn.clicked.connect(self.mostrar_pagina_participantes_actualizar)

        # botones de atras
        self.pagina_crear.ui.BackButton_CreateEvent.clicked.connect(self.mostrar_pagina_crud)
        self.pagina_crear.ui.FinishCreateEvent_Btn.clicked.connect(self.guardar_nuevo_evento)
        self.pagina_actualizar.ui.BackButton_UpdateEvent.clicked.connect(self.mostrar_pagina_crud)
        self.pagina_mesas.ui.BackButton_AssignMenu.clicked.connect(self.mostrar_pagina_crud)
        self.pagina_borrar.ui.BackButton_DeleteEvent.clicked.connect(self.mostrar_pagina_crud)

        # el boton de confirmar para borrar
        self.pagina_borrar.ui.ConfirmDelete_Btn.clicked.connect(self.borrar_evento_seleccionado)

        # el boton de guardar en la ventana de actualizar
        self.pagina_actualizar.ui.SaveUpdate_Btn.clicked.connect(self.guardar_evento_actualizado)
        
        # botones de la pagina 6 (gestionar invitados)
        self.pagina_participantes.ui.Add_Btn.clicked.connect(self.anadir_participante_al_evento)
        
        # si haces doble clic en un invitado
        self.pagina_participantes.ui.List_AllGuests.itemDoubleClicked.connect(self.gestionar_participante_seleccionado)
        
        # si empiezas a escribir un nombre nuevo
        self.pagina_participantes.ui.Input_ParticipantName.textChanged.connect(self.limpiar_participante_en_gestion)

        # los botones v, x y eliminar
        self.pagina_participantes.ui.MoveToPreference_Btn.clicked.connect(self.participante_anadir_preferencia)
        self.pagina_participantes.ui.MoveToAvoid_Btn.clicked.connect(self.participante_anadir_evitado)
        self.pagina_participantes.ui.RemoveFromList_Btn.clicked.connect(self.participante_eliminar_relacion)

        # el boton de atras en la ventana de asignar a mano
        self.pagina_manual.ui.BackButton_ManualAssign.clicked.connect(self.mostrar_pagina_mesas)

        # botones de la ventana de asignar a mano
        self.pagina_manual.ui.NextTable_Btn.clicked.connect(self.manual_siguiente_mesa)
        self.pagina_manual.ui.PrevTable_Btn.clicked.connect(self.manual_anterior_mesa)
        self.pagina_manual.ui.AddParticipant_Btn.clicked.connect(self.manual_anadir_participante)
        self.pagina_manual.ui.RemoveParticipant_Btn.clicked.connect(self.manual_eliminar_participante)

        # el boton de atras en la ventana de resultados
        self.pagina_resultados_auto.ui.BackButton_AutoAssign.clicked.connect(self.mostrar_pagina_mesas)

        # el boton de atras en la ventana de excepciones
        self.pagina_excepciones.ui.BackButton_Exceptions.clicked.connect(self.mostrar_pagina_auto)
        
        # botones de la ventana de excepciones
        self.pagina_excepciones.ui.NextTable_Btn.clicked.connect(self.excepcion_siguiente_mesa)
        self.pagina_excepciones.ui.PrevTable_Btn.clicked.connect(self.excepcion_anterior_mesa)
        self.pagina_excepciones.ui.AddParticipant_Btn.clicked.connect(self.excepcion_anadir_participante)
        self.pagina_excepciones.ui.RemoveParticipant_Btn.clicked.connect(self.excepcion_eliminar_participante)
        
        # el boton de guardar como csv
        self.pagina_crud.ui.GenerateCSV_Btn.clicked.connect(self.generar_csv_evento_seleccionado)
        
        self.resize(904, 617)
        # lee los eventos guardados al abrir
        self.cargar_y_actualizar_eventos()


    # aqui empiezan las funciones
    
    # cambiar a la ventana principal
    def mostrar_pagina_crud(self):
        self.actualizar_tabla_crud()
        self.setCurrentIndex(0)
        
    # cambiar a la ventana de crear
    def mostrar_pagina_crear(self):
        # borra todo lo de antes
        self.evento_en_edicion_actual = None
        self.participante_en_gestion = None
        self.pagina_participantes.ui.Input_ParticipantName.setText("") 
        self.actualizar_listas_participantes() 
        self.setCurrentIndex(1) 

    # cambiar a la ventana de actualizar
    def mostrar_pagina_actualizar(self):
        # pilla la tabla de eventos
        tabla_crud = self.pagina_crud.ui.EventList_Table
        
        # mira que fila ha elegido
        fila_seleccionada = tabla_crud.currentRow()

        # si no ha elegido, avisa
        if fila_seleccionada == -1:
            QMessageBox.warning(self, "Error", "Selecciona un evento para editar")
            return # y no sigue

        # busca el evento en nuestra lista
        try:
            # guarda el evento para saber cual es
            self.evento_en_edicion_actual = self.lista_eventos[fila_seleccionada]
            # borra el invitado que estuvieramos editando
            self.participante_en_gestion = None
            self.pagina_participantes.ui.Input_ParticipantName.setText("") 
            self.actualizar_listas_participantes() 
        except IndexError:
            QMessageBox.critical(self, "Error")
            return

        # rellena los campos con los datos
        self.pagina_actualizar.ui.Input_EventName.setText(self.evento_en_edicion_actual.nombre)
        self.pagina_actualizar.ui.Input_EventDate.setText(self.evento_en_edicion_actual.fecha)
        self.pagina_actualizar.ui.Input_EventLocation.setText(self.evento_en_edicion_actual.ubicacion)
        self.pagina_actualizar.ui.Input_EventOrganizer.setText(self.evento_en_edicion_actual.organizador)
        self.pagina_actualizar.ui.Input_NumTables.setValue(self.evento_en_edicion_actual.numMesas)
        
        # enseña la ventana
        self.setCurrentIndex(2)

    # cambiar a la ventana de asignar mesas
    def mostrar_pagina_mesas(self):

        # pilla la tabla de eventos
        tabla_crud = self.pagina_crud.ui.EventList_Table
        # mira que fila ha elegido
        fila_seleccionada = tabla_crud.currentRow()

        # si no ha elegido evento, avisamos
        if fila_seleccionada == -1:
            QMessageBox.warning(self, "Sin seleccion", "Por favor, selecciona un evento para asignar sus mesas.")
            return

        # pillamos el evento de la lista
        try:
            self.evento_en_edicion_actual = self.lista_eventos[fila_seleccionada]
            print(f"Gestionando mesas para el evento: {self.evento_en_edicion_actual.nombre}")
        except IndexError:
            QMessageBox.critical(self, "Error")
            return # se pira

        # enseña la ventana de asignar mesas
        self.setCurrentIndex(3)

    # enseña la ventana de asignar a mano
    def mostrar_pagina_manual(self):
        # si no hay evento, avisamos y salimos
        if self.evento_en_edicion_actual is None:
            QMessageBox.warning(self, "Error", "No hay evento seleccionado.")
            return
            
        self.mesa_manual_actual_idx = 0 # empezamos por la primera mesa
        self.actualizar_listas_manual() # actualizamos las listas de invitados
        self.setCurrentIndex(4) # enseñamos la ventana 4 (manual)

    # cambiar a la ventana de borrar
    def mostrar_pagina_borrar(self):
        self.setCurrentIndex(5)
        # actualizamos la tabla de borrar eventos
        self.cargar_y_actualizar_eventos_borrar()
    


    # funciones de la ventana de invitados (la de las listas v y x)

    # prepara la ventana de invitados (para crear)
    def preparar_evento_para_participantes(self):
        
        # si no hay evento, lo crea temporal
        if self.evento_en_edicion_actual is None:
            if not self._crear_evento_temporal_desde_pagina1():
                return # si da error, salimos
        
        # recargamos la lista de "todos los invitados"
        self.actualizar_listas_participantes()
        
        # modo "crear"
        self.modo_gestion_participantes = "CREAR" 
        try:
            # por si acaso, desconectamos los botones
            self.pagina_participantes.ui.BackButton_Participants.clicked.disconnect()
            self.pagina_participantes.ui.Finish_Btn.clicked.disconnect()
        except TypeError:
            pass # si no estaban conectados, no pasa nada
            
        # boton atras vuelve a "crear"
        self.pagina_participantes.ui.BackButton_Participants.clicked.connect(self.mostrar_pagina_crear)
        # boton finalizar guarda todo
        self.pagina_participantes.ui.Finish_Btn.clicked.connect(self.guardar_evento_y_participantes)
        
        self.setCurrentIndex(6) # enseña la ventana 6 (invitados)

    # prepara la ventana de invitados (para actualizar)
    def mostrar_pagina_participantes_actualizar(self):
        
        # si no hay evento seleccionado, avisamos
        if self.evento_en_edicion_actual is None:
            QMessageBox.critical(self, "Error", "No hay ningun evento seleccionado. Esto no deberia pasar.")
            return

        # actualiza las listas
        self.actualizar_listas_participantes()
        
        # modo "actualizar"
        self.modo_gestion_participantes = "ACTUALIZAR" 
        try:
            # limpia los botones
            self.pagina_participantes.ui.BackButton_Participants.clicked.disconnect()
            self.pagina_participantes.ui.Finish_Btn.clicked.disconnect()
        except TypeError:
            pass # no pasa nada
            
        # el boton de atras vuelve a la ventana de actualizar
        self.pagina_participantes.ui.BackButton_Participants.clicked.connect(self.mostrar_pagina_actualizar)
        # el boton de finalizar solo vuelve, no guarda
        self.pagina_participantes.ui.Finish_Btn.clicked.connect(self.mostrar_pagina_actualizar)
        
        self.setCurrentIndex(6) # enseña la ventana 6

    # añade un invitado nuevo (boton añadir)
    def anadir_participante_al_evento(self):
        
        # 1. si no hay evento, lo crea temporal
        if self.evento_en_edicion_actual is None:
             if not self._crear_evento_temporal_desde_pagina1():
                return # si falla se pira
        
        # 2. pilla el nombre del campo
        nombre_participante = self.pagina_participantes.ui.Input_ParticipantName.text().strip()
        # si no has escrito nada, te aviso
        if not nombre_participante:
            QMessageBox.warning(self, "Oye", "Escribe el nombre del participante.")
            return
            
        # 3. mira si esta repe
        for p in self.evento_en_edicion_actual.participantes:
            if p.nombre.lower() == nombre_participante.lower():
                QMessageBox.warning(self, "Duplicado", f"El participante '{nombre_participante}' ya existe en este evento.")
                return

        # 4. crea un id unico
        evento_id = self.evento_en_edicion_actual.IdEvento
        num_part = len(self.evento_en_edicion_actual.participantes)
        participante_id = f"{evento_id}_p_{num_part + 1}"

        # crea el invitado
        nuevo_participante = Participante(participante_id, nombre_participante)
        # lo mete en la lista de invitados del evento
        self.evento_en_edicion_actual.anadirparticipante(nuevo_participante)
        
        # 5. lo marca como "invitado actual"
        self.participante_en_gestion = nuevo_participante
        
        # 6. recarga la lista "todos"
        self.actualizar_listas_participantes()
        
        # 7. lo busca y lo pone en azul
        for i in range(self.pagina_participantes.ui.List_AllGuests.count()):
            item = self.pagina_participantes.ui.List_AllGuests.item(i)
            if item.text() == nombre_participante:
                item.setSelected(True)
                # cargamos sus listas de preferencias (vacias)
                self.actualizar_listas_preferencias()
                break
        
        # 8. si estamos en modo "actualizar", guarda
        if self.modo_gestion_participantes == "ACTUALIZAR":
            self.gestor_datos.guardarEventos(self.lista_eventos)

    # refresca las listas de invitados
    def actualizar_listas_participantes(self):
        lista_invitados = self.pagina_participantes.ui.List_AllGuests
        lista_pref = self.pagina_participantes.ui.List_Preference
        lista_no = self.pagina_participantes.ui.List_Avoid
        
        # vacia las tres listas
        lista_invitados.clear()
        lista_pref.clear()
        lista_no.clear()

        # si estamos en un evento...
        if self.evento_en_edicion_actual:
            # metemos cada invitado en la lista de "todos"
            for participante in self.evento_en_edicion_actual.participantes:
                lista_invitados.addItem(participante.nombre)
        
        # quita la seleccion (que no haya nada en azul)
        self.pagina_participantes.ui.List_AllGuests.clearSelection()
        
    # guarda el evento nuevo (boton finalizar)
    def guardar_evento_y_participantes(self):
        if self.evento_en_edicion_actual is None:
            QMessageBox.critical(self, "Error", "No hay evento que guardar.")
            return
            
        # mira si el evento ya esta en la lista (por si acaso)
        evento_existe = False
        for ev in self.lista_eventos:
            if ev.IdEvento == self.evento_en_edicion_actual.IdEvento:
                evento_existe = True
                break
        
        # si no estaba, lo añade
        if not evento_existe:
             self.lista_eventos.append(self.evento_en_edicion_actual)
        
        # guarda en el json
        self.gestor_datos.guardarEventos(self.lista_eventos)

        # limpia las variables
        self.evento_en_edicion_actual = None
        self.participante_en_gestion = None 
        
        # limpia los campos de "crear"
        self.pagina_crear.ui.Input_EventName.setText("")
        self.pagina_crear.ui.Input_EventDate.setText("")
        self.pagina_crear.ui.Input_EventLocation.setText("")
        self.pagina_crear.ui.Input_EventOrganizer.setText("")
        self.pagina_crear.ui.Input_NumTables.setValue(1)
        
        # limpia la ventana de invitados
        self.pagina_participantes.ui.Input_ParticipantName.setText("")
        self.actualizar_listas_participantes()

        # vuelve al menu principal
        self.mostrar_pagina_crud()


    # funciones de guardar, borrar y cargar

    # guarda un evento que estabamos editando
    def guardar_evento_actualizado(self):

        # pilla los datos de los campos
        nuevo_nombre = self.pagina_actualizar.ui.Input_EventName.text()
        nueva_fecha = self.pagina_actualizar.ui.Input_EventDate.text()
        nueva_ubicacion = self.pagina_actualizar.ui.Input_EventLocation.text()
        nuevo_organizador = self.pagina_actualizar.ui.Input_EventOrganizer.text()
        nuevo_numMesas = self.pagina_actualizar.ui.Input_NumTables.value()

        # si falta nombre o fecha, avisa
        if not nuevo_nombre or not nueva_fecha:
            QMessageBox.warning(self,  "Oye", "Pon el nombre y la fecha")       
            return # y salimos

        # actualiza el objeto
        self.evento_en_edicion_actual.nombre = nuevo_nombre
        self.evento_en_edicion_actual.fecha = nueva_fecha
        self.evento_en_edicion_actual.ubicacion = nueva_ubicacion
        self.evento_en_edicion_actual.organizador = nuevo_organizador

        # si cambia el numero de mesas
        if self.evento_en_edicion_actual.numMesas != nuevo_numMesas:
            # actualiza el numero
            self.evento_en_edicion_actual.numMesas = nuevo_numMesas
            # borra las mesas viejas
            self.evento_en_edicion_actual.mesas = []
            capacidad_por_mesa = 10 # 10 sitios por mesa
            # crea las mesas nuevas vacias
            for i in range(nuevo_numMesas):
                id_mesa = f"{self.evento_en_edicion_actual.IdEvento}_mesa_{i+1}"
                nueva_mesa = Mesa(id_mesa=id_mesa, numero=i+1, capacidad=capacidad_por_mesa)
                self.evento_en_edicion_actual.mesas.append(nueva_mesa)
            QMessageBox.warning(self,"Oye", "Se restauraron las mesas tendras que asignar de nuevo")       

        # guarda en el json
        self.gestor_datos.guardarEventos(self.lista_eventos)
        # limpia el evento temporal
        self.evento_en_edicion_actual = None
        # vuelve al menu
        self.mostrar_pagina_crud()


    # borra el evento seleccionado
    def borrar_evento_seleccionado(self):

        # pilla la tabla de "borrar"
        tabla_borrar = self.pagina_borrar.ui.EventList_Table_Delete
        
        # mira que fila ha elegido
        fila_seleccionada = tabla_borrar.currentRow()

        # si no ha elegido, avisa
        if fila_seleccionada == -1:
            QMessageBox.warning(self, "Oye", "No has seleccionado ningun evento.")
            return

        # pilla el evento de nuestra lista
        try:
            evento_a_borrar = self.lista_eventos[fila_seleccionada]
            nombre_evento = evento_a_borrar.nombre
        except IndexError:
            QMessageBox.critical(self, "Error", "no se ha podido borrar")
            return

        # pide confirmacion
        confirmacion = QMessageBox.question(
            self,
            "Confirmar borrado",
            f"¿Estas seguro de que quieres borrar el evento '{nombre_evento}'?\n\nEsta accion no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No # "no" por defecto
        )

        # si dice que si
        if confirmacion == QMessageBox.Yes:
            # lo quita de la lista
            self.lista_eventos.pop(fila_seleccionada)
            
            # guarda en el json
            self.gestor_datos.guardarEventos(self.lista_eventos)
            
            # actualiza la tabla de borrar
            self.actualizar_tabla_borrar()

            # vuelve al menu
            self.mostrar_pagina_crud()
            
        else:
            # si dice "no", no hace nada
            return

    # lee eventos.json y rellena la tabla principal
    def cargar_y_actualizar_eventos(self):
        self.lista_eventos = self.gestor_datos.cargarEventos()
        self.actualizar_tabla_crud()

    # lee eventos.json y rellena la tabla de borrar
    def cargar_y_actualizar_eventos_borrar(self):
        self.lista_eventos = self.gestor_datos.cargarEventos()
        self.actualizar_tabla_borrar()

    # guarda un evento (si no se entro a "añadir invitados")
    def guardar_nuevo_evento(self):
        # pilla los datos de los campos
        nombre = self.pagina_crear.ui.Input_EventName.text()
        fecha = self.pagina_crear.ui.Input_EventDate.text()
        ubicacion = self.pagina_crear.ui.Input_EventLocation.text()
        organizador = self.pagina_crear.ui.Input_EventOrganizer.text()
        numMesas = self.pagina_crear.ui.Input_NumTables.value()

        # si falta nombre o fecha te avisa
        if not nombre or not fecha:
            QMessageBox.warning(self,  "Oye", "Pon el nombre y la fecha")       
            return
            
        # mira si ya habia uno temporal (del csv)
        if self.evento_en_edicion_actual and self.evento_en_edicion_actual.nombre == nombre:
            nuevo_evento = self.evento_en_edicion_actual
            # actualiza los datos por si los cambio
            nuevo_evento.fecha = fecha
            nuevo_evento.ubicacion = ubicacion
            nuevo_evento.organizador = organizador
            nuevo_evento.numMesas = numMesas
        else:
        # si no, crea uno nuevo
            # crea un id
            nuevo_id = f"evento_{len(self.lista_eventos) + 1}"

            # crea el objeto evento
            try:
                nuevo_evento = Evento(
                    IdEvento=nuevo_id,
                    nombre=nombre,
                    fecha=fecha,
                    ubicacion=ubicacion,
                    organizador=organizador,
                    numMesas=numMesas
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", "No se ha podido crear el evento")
                return

        # lo añade a la lista
        self.lista_eventos.append(nuevo_evento)

        # guarda en el json
        self.gestor_datos.guardarEventos(self.lista_eventos)


        # limpia los campos de "crear"
        self.pagina_crear.ui.Input_EventName.setText("")
        self.pagina_crear.ui.Input_EventDate.setText("")
        self.pagina_crear.ui.Input_EventLocation.setText("")
        self.pagina_crear.ui.Input_EventOrganizer.setText("")
        self.pagina_crear.ui.Input_NumTables.setValue(1)
        
        # limpia las variables
        self.evento_en_edicion_actual = None
        self.participante_en_gestion = None
        self.pagina_participantes.ui.Input_ParticipantName.setText("")
        self.actualizar_listas_participantes()

        # vuelve al menu
        self.mostrar_pagina_crud()

    # funciones para rellenar las tablas
    
    # rellena la tabla de la ventana principal
    def actualizar_tabla_crud(self):

        # pilla la tabla
        tabla = self.pagina_crud.ui.EventList_Table
        
        # bloquea para que no se raye
        tabla.blockSignals(True)
        
        # borra todo
        tabla.setRowCount(0) 
        
        # va fila por fila rellenando
        for evento in self.lista_eventos:
            # mira cuantas filas hay
            row_position = tabla.rowCount()
            # añade una fila al final
            tabla.insertRow(row_position)
            
            # pone los datos en las columnas
            tabla.setItem(row_position, 0, QTableWidgetItem(evento.nombre))
            tabla.setItem(row_position, 1, QTableWidgetItem(evento.fecha))
            tabla.setItem(row_position, 2, QTableWidgetItem(evento.ubicacion))
            tabla.setItem(row_position, 3, QTableWidgetItem(evento.organizador))
            
        # desbloquea
        tabla.blockSignals(False)
        
        # ajusta las columnas al texto
        tabla.resizeColumnsToContents()

    # rellena la tabla de borrar
    def actualizar_tabla_borrar(self):
        # es igual que la de la ventana principal
        tabla = self.pagina_borrar.ui.EventList_Table_Delete
        tabla.blockSignals(True)
        tabla.setRowCount(0)
         # recorre los eventos
        for evento in self.lista_eventos:
            # pilla la posicion
            row_position = tabla.rowCount()
            # mete una fila nueva
            tabla.insertRow(row_position)

            # rellena las celdas
            tabla.setItem(row_position, 0, QTableWidgetItem(evento.nombre))
            tabla.setItem(row_position, 1, QTableWidgetItem(evento.fecha))
            tabla.setItem(row_position, 2, QTableWidgetItem(evento.ubicacion))
            tabla.setItem(row_position, 3, QTableWidgetItem(evento.organizador))
            
        tabla.blockSignals(False) 

    
    # enseña la ventana de resultados automaticos
    def mostrar_pagina_auto(self):
        self.setCurrentIndex(7)

    # enseña la ventana de excepciones
    def mostrar_pagina_excepciones(self):
        if self.evento_en_edicion_actual is None:
            return
            
        self.excepcion_mesa_actual_idx = 0 # empieza en la primera mesa
        self.actualizar_listas_excepciones_ui()
        self.setCurrentIndex(8)


    # el algoritmo magico de google
    def algoritmo_asignar_mesas(self, participantes, mesas):
        """
        algoritmo de asignacion usando or-tools.
        intenta que las mesas queden igualadas.
        """
        model = cp_model.CpModel()

        # 1. mapas para encontrar las cosas rapido
        map_idx_participante = {i: p for i, p in enumerate(participantes)}
        map_idx_mesa = {i: m for i, m in enumerate(mesas)}
        map_nombre_idx_p = {p.nombre: i for i, p in map_idx_participante.items()}
        
        num_participantes = len(participantes)
        num_mesas = len(mesas)

        # 2. variables de decision (quien va a que mesa)
        x = {}
        for p_idx in range(num_participantes):
            for m_idx in range(num_mesas):
                x[p_idx, m_idx] = model.NewBoolVar(f'x_{p_idx}_{m_idx}')

        # 3. variables para equilibrar las mesas
        occupancy = {}
        occupancy_sq = {}

        for m_idx in range(num_mesas):
            capacidad = map_idx_mesa[m_idx].capacidad
            
            # esta variable guarda cuantos hay en la mesa 'm'
            occupancy[m_idx] = model.NewIntVar(0, capacidad, f'occ_{m_idx}')
            model.Add(occupancy[m_idx] == sum(x[p_idx, m_idx] for p_idx in range(num_participantes)))

            # truco matematico: (5, 5) es mejor que (10, 0)
            occupancy_sq[m_idx] = model.NewIntVar(0, capacidad * capacidad, f'occ_sq_{m_idx}')
            model.AddMultiplicationEquality(occupancy_sq[m_idx], [occupancy[m_idx], occupancy[m_idx]])

        # 4. las reglas (lo obligatorio)

        # un invitado solo en 1 mesa
        for p_idx in range(num_participantes):
            model.Add(sum(x[p_idx, m_idx] for m_idx in range(num_mesas)) <= 1)

        # los que se odian no van juntos
        for p1_idx, p1_obj in map_idx_participante.items():
            for nombre_evitado in p1_obj.evitados:
                if nombre_evitado in map_nombre_idx_p:
                    p2_idx = map_nombre_idx_p[nombre_evitado]
                    for m_idx in range(num_mesas):
                        # la suma de los dos en una mesa no puede ser 2
                        model.Add(x[p1_idx, m_idx] + x[p2_idx, m_idx] <= 1)

        # 5. objetivos (lo que queremos conseguir)
        puntuacion_total = []

        # a. lo mas importante: sentar a todos
        for p_idx in range(num_participantes):
            for m_idx in range(num_mesas):
                puntuacion_total.append(x[p_idx, m_idx] * 100000)

        # b. que los amigos se sienten juntos
        for p1_idx, p1_obj in map_idx_participante.items():
            for nombre_preferido in p1_obj.preferencias:
                if nombre_preferido in map_nombre_idx_p:
                    p2_idx = map_nombre_idx_p[nombre_preferido]
                    if p1_idx < p2_idx: # para no contarlo dos veces
                        for m_idx in range(num_mesas):
                            juntos = model.NewBoolVar(f'juntos_{p1_idx}_{p2_idx}_{m_idx}')
                            # "juntos" vale 1 si los dos estan en la mesa
                            model.Add(x[p1_idx, m_idx] + x[p2_idx, m_idx] == 2).OnlyEnforceIf(juntos)
                            model.Add(x[p1_idx, m_idx] + x[p2_idx, m_idx] != 2).OnlyEnforceIf(juntos.Not())
                            puntuacion_total.append(juntos * 500)

        # c. que las mesas esten igualadas
        for m_idx in range(num_mesas):
            puntuacion_total.append(occupancy_sq[m_idx] * -5)

        # busca la maxima puntuacion
        model.Maximize(sum(puntuacion_total))

        # 6. resolver
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        # si encuentra solucion
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print("¡distribucion equilibrada encontrada!")
            for p_idx in range(num_participantes):
                for m_idx in range(num_mesas):
                    if solver.Value(x[p_idx, m_idx]) == 1:
                        participante = map_idx_participante[p_idx]
                        mesa = map_idx_mesa[m_idx]
                        # añade el invitado a la mesa
                        mesa.anadirParticipante(participante)
                        participante.asignar_mesa(mesa.id_mesa)
                        break 
            return True
        else:
            # si no encuentra
            print("no se encontro solucion valida.")
            return False


    # funcion del boton "asignar automatico"
    def ejecutar_asignacion_automatica(self):
        # miramos si hay un evento cargado
        if self.evento_en_edicion_actual is None:
            QMessageBox.critical(self, "Error", "No hay evento seleccionado.")
            return

        print(f"iniciando asignacion automatica para: {self.evento_en_edicion_actual.nombre}")

        # 1. vacia las mesas (por si acaso)
        for mesa in self.evento_en_edicion_actual.mesas:
            mesa.participantes = []
        for p in self.evento_en_edicion_actual.participantes:
            p.quitar_mesa()

        # 2. prepara las listas
        participantes = list(self.evento_en_edicion_actual.participantes)
        mesas = list(self.evento_en_edicion_actual.mesas)

        if not participantes:
            QMessageBox.warning(self, "Vacio", "No hay participantes para asignar.")
            return
        if not mesas:
            QMessageBox.warning(self, "Vacio", "No hay mesas para asignar.")
            return

        # 3. llama al algoritmo
        solucion_encontrada = self.algoritmo_asignar_mesas(participantes, mesas)

        # si falla, avisa
        if not solucion_encontrada:
            QMessageBox.warning(self, "Asignacion fallida", 
                            "no se pudo encontrar una solucion optima.\n"
                            "los participantes sin mesa se moveran a excepciones.")

        # 4. guarda en el json
        self.gestor_datos.guardarEventos(self.lista_eventos)
        
        # 5. refresca las ventanas
        self.actualizar_tabla_resultados_auto()
        self.actualizar_lista_excepciones() # recalcula la lista de excepciones

        # enseña la ventana de resultados
        self.setCurrentIndex(7)


    # rellena la tabla de resultados
    def actualizar_tabla_resultados_auto(self):
        tabla = self.pagina_resultados_auto.ui.Results_Table
        tabla.blockSignals(True)
        tabla.setRowCount(0)

        if self.evento_en_edicion_actual:
            # vamos mesa por mesa
            for mesa in self.evento_en_edicion_actual.mesas:
                row_position = tabla.rowCount()
                tabla.insertRow(row_position)

                # columna 1: "mesa 1 (5/10)"
                texto_mesa = f"Mesa {mesa.numero} ({len(mesa.participantes)}/{mesa.capacidad})"
                tabla.setItem(row_position, 0, QTableWidgetItem(texto_mesa))

                # columna 2: "ana, jose, juan..."
                nombres = [p.nombre for p in mesa.participantes]
                texto_nombres = ", ".join(nombres)
                tabla.setItem(row_position, 1, QTableWidgetItem(texto_nombres))

        tabla.blockSignals(False)
        # ajustamos el ancho
        tabla.resizeColumnsToContents()


    # rellena la lista de los que se quedaron fuera
    def actualizar_lista_excepciones(self):
        lista = self.pagina_excepciones.ui.List_Exceptions
        lista.clear()
        
        # la borra y la vuelve a crear
        self.lista_excepciones = [] 
        
        if self.evento_en_edicion_actual:
            for participante in self.evento_en_edicion_actual.participantes:
                # si no tiene mesa, es una excepcion
                if participante.mesa_asignada is None:
                    self.lista_excepciones.append(participante)
                    lista.addItem(participante.nombre)

    # funciones para csv y otras cosas
    
    # funcion ayudante: crea un evento temporal (sin guardar)
    def _crear_evento_temporal_desde_pagina1(self):
        # pilla los datos de "crear evento"
        nombre = self.pagina_crear.ui.Input_EventName.text().strip()
        fecha = self.pagina_crear.ui.Input_EventDate.text().strip()
        
        # si falta nombre o fecha, avisa y devuelve 'false'
        if not nombre or not fecha:
            QMessageBox.warning(self, "Datos incompletos", 
                            "debes completar al menos el nombre y la fecha.")
            return False
        
        ubicacion = self.pagina_crear.ui.Input_EventLocation.text().strip()
        organizador = self.pagina_crear.ui.Input_EventOrganizer.text().strip()
        numMesas = self.pagina_crear.ui.Input_NumTables.value()
        nuevo_id = f"evento_{len(self.lista_eventos) + 1}"
        
        # crea el evento y lo guarda en la variable
        try:
            self.evento_en_edicion_actual = Evento(
                IdEvento=nuevo_id,
                nombre=nombre,
                fecha=fecha,
                ubicacion=ubicacion,
                organizador=organizador,
                numMesas=numMesas
            )
            return True # devuelve 'true' si todo ok
        except Exception as e:
            QMessageBox.critical(self, "Error", f"no se pudo crear el evento temporal.\n{e}")
            return False
    
    # funcion del boton "subir csv"
    def cargar_participantes_csv(self):
        pagina_actual = self.currentIndex()

        # 1. comprueba que hay un evento
        if pagina_actual == 1: # si estamos en "crear"
            # si no hay evento temporal
            if self.evento_en_edicion_actual is None:
                # intenta crearlo
                if not self._crear_evento_temporal_desde_pagina1():
                    return # si falla, salimos
        
        elif pagina_actual == 2: # si estamos en "actualizar"
            if self.evento_en_edicion_actual is None:
                QMessageBox.critical(self, "Error", "no hay evento seleccionado")
                return
        
        # 2. abre el explorador de archivos
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(self, "Seleccionar CSV de Participantes", "", "Archivos CSV (*.csv);;Todos los archivos (*)", options=options)

        # si cancela, se pira
        if not filePath:
            return

        # 3. lee el archivo
        try:
            participantes_cargados = 0
            with open(filePath, mode='r', encoding='utf-8') as f:
                # la primera fila son los titulos
                reader = csv.DictReader(f)
                
                # fila por fila
                for row in reader:
                    # pilla el nombre
                    nombre_participante = row.get('Nombre') or row.get('nombre')
                    
                    # si la fila esta vacia, la salta
                    if not nombre_participante:
                        continue
                        
                    # crea un id
                    evento_id = self.evento_en_edicion_actual.IdEvento
                    num_part = len(self.evento_en_edicion_actual.participantes)
                    participante_id = f"{evento_id}_p_{num_part + 1}"
                    
                    # crea el invitado
                    nuevo_participante = Participante(participante_id, nombre_participante)

                    # pilla las preferencias
                    pref_texto = row.get('Preferencias') or row.get('preferencias', '')
                    if pref_texto:
                        # las separa por punto y coma
                        lista_pref = [nombre.strip() for nombre in pref_texto.split(';') if nombre.strip()]
                        nuevo_participante.preferencias = lista_pref

                    # pilla los evitados
                    evit_texto = row.get('Evitados') or row.get('evitados', '')
                    if evit_texto:
                        # las separa por punto y coma
                        lista_evit = [nombre.strip() for nombre in evit_texto.split(';') if nombre.strip()]
                        nuevo_participante.evitados = lista_evit
                    
                    # lo añade al evento
                    self.evento_en_edicion_actual.anadirparticipante(nuevo_participante)
                    participantes_cargados += 1

            # avisa de que todo ok
            QMessageBox.information(self, "Exito", f"Se han cargado {participantes_cargados} participantes desde el CSV.")
            
            # si estabamos en "actualizar", guarda
            if pagina_actual == 2:
                self.gestor_datos.guardarEventos(self.lista_eventos)

        except Exception as e:
            # si falla algo, avisa
            QMessageBox.critical(self, "Error al leer CSV", f"No se pudo leer el archivo.\nError: {e}")

    
    # funciones de "asignar manual"

    # rellena las listas de "asignar manual"
    def actualizar_listas_manual(self):
        if not self.evento_en_edicion_actual or not self.evento_en_edicion_actual.mesas:
            return

        # 1. pilla la mesa que estamos viendo
        mesa_actual = self.evento_en_edicion_actual.mesas[self.mesa_manual_actual_idx]
        # pone el titulo "mesa 1 (3/10)"
        self.pagina_manual.ui.Label_TableParticipants.setText(f"Mesa {mesa_actual.numero} ({len(mesa_actual.participantes)}/{mesa_actual.capacidad})")

        # 2. rellena la lista de "en mesa"
        lista_mesa_ui = self.pagina_manual.ui.List_TableParticipants
        lista_mesa_ui.clear()
        for p in mesa_actual.participantes:
            lista_mesa_ui.addItem(p.nombre)

        # 3. rellena la lista de "sin asignar"
        lista_sin_asignar_ui = self.pagina_manual.ui.List_UnassignedGuests
        lista_sin_asignar_ui.clear()
        
        # crea una lista rapida de los que ya estan sentados
        participantes_asignados_ids = set()
        for m in self.evento_en_edicion_actual.mesas:
            for p in m.participantes:
                participantes_asignados_ids.add(p.id_participante)

        # mira todos los invitados
        for p in self.evento_en_edicion_actual.participantes:
            # si no esta en la lista de sentados
            if p.id_participante not in participantes_asignados_ids:
                # lo añade a "sin asignar"
                lista_sin_asignar_ui.addItem(p.nombre)

    # boton "siguiente mesa" (manual)
    def manual_siguiente_mesa(self):
        if not self.evento_en_edicion_actual: return
        num_mesas = len(self.evento_en_edicion_actual.mesas)
        if num_mesas > 0:
            # pasa a la siguiente mesa
            self.mesa_manual_actual_idx = (self.mesa_manual_actual_idx + 1) % num_mesas
            # y refresca las listas
            self.actualizar_listas_manual()

    # boton "anterior mesa" (manual)
    def manual_anterior_mesa(self):
        if not self.evento_en_edicion_actual: return
        num_mesas = len(self.evento_en_edicion_actual.mesas)
        if num_mesas > 0:
            # pasa a la mesa anterior
            self.mesa_manual_actual_idx = (self.mesa_manual_actual_idx - 1) % num_mesas
            # y refresca las listas
            self.actualizar_listas_manual()

    # boton "añadir" (manual)
    def manual_anadir_participante(self):
        # pilla el invitado de "sin asignar"
        item_seleccionado = self.pagina_manual.ui.List_UnassignedGuests.currentItem()
        if not item_seleccionado or not self.evento_en_edicion_actual:
            return

        # pilla la mesa que estamos viendo
        mesa_actual = self.evento_en_edicion_actual.mesas[self.mesa_manual_actual_idx]
        # si la mesa esta llena, avisa
        if mesa_actual.estaLlena():
            QMessageBox.warning(self, "Mesa Llena", f"La Mesa {mesa_actual.numero} ya esta llena.")
            return

        # busca el invitado en la lista
        nombre_p = item_seleccionado.text()
        participante_a_mover = None
        
        # comprueba otra vez que no este asignado
        participantes_asignados_ids = set()
        for m in self.evento_en_edicion_actual.mesas:
            for p in m.participantes:
                participantes_asignados_ids.add(p.id_participante)
        
        for p in self.evento_en_edicion_actual.participantes:
            if p.nombre == nombre_p and p.id_participante not in participantes_asignados_ids:
                participante_a_mover = p
                break
        
        # si lo encuentra...
        if participante_a_mover:
            # lo mete en la mesa
            mesa_actual.anadirParticipante(participante_a_mover)
            # guarda el id de la mesa en el invitado
            participante_a_mover.asignar_mesa(mesa_actual.id_mesa)
            # refresca las listas
            self.actualizar_listas_manual()
            # guarda en el json
            self.gestor_datos.guardarEventos(self.lista_eventos)

    # boton "eliminar" (manual)
    def manual_eliminar_participante(self):
        # pilla el invitado de "en mesa"
        item_seleccionado = self.pagina_manual.ui.List_TableParticipants.currentItem()
        if not item_seleccionado or not self.evento_en_edicion_actual:
            return

        mesa_actual = self.evento_en_edicion_actual.mesas[self.mesa_manual_actual_idx]
        
        # busca el objeto invitado
        nombre_p = item_seleccionado.text()
        participante_a_mover = None
        for p in mesa_actual.participantes:
            if p.nombre == nombre_p:
                participante_a_mover = p
                break

        if participante_a_mover:
            # lo saca de la mesa
            mesa_actual.eliminarParticipante(participante_a_mover)
            # le borra la mesa al invitado
            participante_a_mover.quitar_mesa()
            # refresca las listas
            self.actualizar_listas_manual()
            # guarda en el json
            self.gestor_datos.guardarEventos(self.lista_eventos)

    # funciones de "gestionar participante"

    # se activa cuando escribes en el nombre
    def limpiar_participante_en_gestion(self, texto):
        # si escribe, borra la seleccion azul
        if self.participante_en_gestion and texto != self.participante_en_gestion.nombre:
            self.participante_en_gestion = None
            self.pagina_participantes.ui.List_AllGuests.clearSelection()
            self.actualizar_listas_preferencias()

    # se activa al hacer doble clic en un invitado
    def gestionar_participante_seleccionado(self, item):
        # carga este invitado para editarlo
        if item is None:
            self.participante_en_gestion = None
            self.pagina_participantes.ui.Input_ParticipantName.setText("")
            self.actualizar_listas_preferencias()
            return
            
        nombre_p = item.text()
        self.participante_en_gestion = None
        
        if self.evento_en_edicion_actual:
            for p in self.evento_en_edicion_actual.participantes:
                if p.nombre == nombre_p:
                    # lo carga para editarlo
                    self.participante_en_gestion = p
                    break
        
        if self.participante_en_gestion:
            # pone el nombre en el campo
            self.pagina_participantes.ui.Input_ParticipantName.setText(self.participante_en_gestion.nombre)
            # rellena sus listas de pref/evitados
            self.actualizar_listas_preferencias()

    # rellena las listas de pref/evitados
    def actualizar_listas_preferencias(self):
        lista_pref = self.pagina_participantes.ui.List_Preference
        lista_evit = self.pagina_participantes.ui.List_Avoid
        
        # vacia las listas
        lista_pref.clear()
        lista_evit.clear()

        # si tenemos un invitado cargado
        if self.participante_en_gestion:
            # rellenamos las listas con sus datos
            for nombre_pref in self.participante_en_gestion.preferencias:
                lista_pref.addItem(nombre_pref)
            for nombre_evit in self.participante_en_gestion.evitados:
                lista_evit.addItem(nombre_evit)

    # boton verde (v)
    def participante_anadir_preferencia(self):
        # si no hay invitado (doble clic), avisa
        if not self.participante_en_gestion:
            QMessageBox.warning(self, "Error", "primero añade o selecciona (doble clic) un participante para editarlo.")
            return

        # pilla el invitado (un clic)
        item_seleccionado = self.pagina_participantes.ui.List_AllGuests.currentItem()
        if not item_seleccionado:
            QMessageBox.warning(self, "Error", "ahora, selecciona (un clic) a otro participante de la lista 'todos' para añadirlo.")
            return
            
        nombre_a_anadir = item_seleccionado.text()

        # no puedes añadirte a ti mismo
        if nombre_a_anadir == self.participante_en_gestion.nombre:
            QMessageBox.warning(self, "Error", "no puedes añadirte a ti mismo.")
            return
            
        # lo añade a la lista
        if self.participante_en_gestion.anadir_preferencia(nombre_a_anadir):
            # lo quita de evitados (por si acaso)
            self.participante_en_gestion.eliminar_evitado(nombre_a_anadir)
            self.actualizar_listas_preferencias() # refresca las listas
            
            # si estamos en modo "actualizar", guarda
            if self.modo_gestion_participantes == "ACTUALIZAR":
                self.gestor_datos.guardarEventos(self.lista_eventos)

    # boton rojo (x)
    def participante_anadir_evitado(self):
        # si no hay invitado (doble clic), avisa
        if not self.participante_en_gestion:
            QMessageBox.warning(self, "Error", "primero añade o selecciona (doble clic) un participante para editarlo.")
            return

        # pilla el invitado (un clic)
        item_seleccionado = self.pagina_participantes.ui.List_AllGuests.currentItem()
        if not item_seleccionado:
            QMessageBox.warning(self, "Error", "ahora, selecciona (un clic) a otro participante de la lista 'todos' para añadirlo.")
            return

        nombre_a_anadir = item_seleccionado.text()

        # no puedes evitarte a ti mismo
        if nombre_a_anadir == self.participante_en_gestion.nombre:
            QMessageBox.warning(self, "Error", "no puedes evitarte a ti mismo.")
            return

        # lo añade a la lista
        if self.participante_en_gestion.anadir_evitado(nombre_a_anadir):
            # lo quita de preferencias (por si acaso)
            self.participante_en_gestion.eliminar_preferencia(nombre_a_anadir)
            self.actualizar_listas_preferencias() # refresca las listas
            
            # si estamos en modo "actualizar", guarda
            if self.modo_gestion_participantes == "ACTUALIZAR":
                self.gestor_datos.guardarEventos(self.lista_eventos)

    # boton "eliminar" (pagina 6)
    def participante_eliminar_relacion(self):
        if not self.participante_en_gestion:
            QMessageBox.warning(self, "Error", "no hay ningun participante seleccionado para editar.")
            return

        # mira si esta seleccionado en la lista "preferencia"
        item_pref = self.pagina_participantes.ui.List_Preference.currentItem()
        if item_pref:
            # si es asi, lo borra
            self.participante_en_gestion.eliminar_preferencia(item_pref.text())
            self.actualizar_listas_preferencias()
            return

        # mira si esta seleccionado en la lista "no acepta"
        item_evit = self.pagina_participantes.ui.List_Avoid.currentItem()
        if item_evit:
            # si es asi, lo borra
            self.participante_en_gestion.eliminar_evitado(item_evit.text())
            self.actualizar_listas_preferencias()
            return

    # funciones de la ventana "excepciones"
    
    # rellena las listas de la ventana "excepciones"
    def actualizar_listas_excepciones_ui(self):
        if not self.evento_en_edicion_actual or not self.evento_en_edicion_actual.mesas:
            return

        # 1. pilla la mesa que estamos viendo
        mesa_actual = self.evento_en_edicion_actual.mesas[self.excepcion_mesa_actual_idx]
        self.pagina_excepciones.ui.Label_TableParticipants.setText(f"Mesa {mesa_actual.numero} ({len(mesa_actual.participantes)}/{mesa_actual.capacidad})")

        # 2. rellena la lista de "participantes en mesa"
        lista_mesa_ui = self.pagina_excepciones.ui.List_TableParticipants
        lista_mesa_ui.clear()
        for p in mesa_actual.participantes:
            lista_mesa_ui.addItem(p.nombre)

        # 3. rellena la lista de "participantes con conflicto"
        lista_excepciones_ui = self.pagina_excepciones.ui.List_Exceptions
        lista_excepciones_ui.clear()
        # usa la lista 'self.lista_excepciones'
        for p in self.lista_excepciones:
            lista_excepciones_ui.addItem(p.nombre)

    # boton "siguiente mesa" (excepciones)
    def excepcion_siguiente_mesa(self):
        if not self.evento_en_edicion_actual: return
        num_mesas = len(self.evento_en_edicion_actual.mesas)
        if num_mesas > 0:
            self.excepcion_mesa_actual_idx = (self.excepcion_mesa_actual_idx + 1) % num_mesas
            self.actualizar_listas_excepciones_ui()

    # boton "anterior mesa" (excepciones)
    def excepcion_anterior_mesa(self):
        if not self.evento_en_edicion_actual: return
        num_mesas = len(self.evento_en_edicion_actual.mesas)
        if num_mesas > 0:
            self.excepcion_mesa_actual_idx = (self.excepcion_mesa_actual_idx - 1) % num_mesas
            self.actualizar_listas_excepciones_ui()

    # boton "añadir" (excepciones)
    def excepcion_anadir_participante(self):
        # pilla el de la lista "conflictos"
        item_seleccionado = self.pagina_excepciones.ui.List_Exceptions.currentItem()
        if not item_seleccionado or not self.evento_en_edicion_actual:
            return

        mesa_actual = self.evento_en_edicion_actual.mesas[self.excepcion_mesa_actual_idx]
        # si la mesa esta llena, avisa
        if mesa_actual.estaLlena():
            QMessageBox.warning(self, "Mesa Llena", f"La Mesa {mesa_actual.numero} ya esta llena.")
            return

        # busca el invitado en la lista de excepciones
        nombre_p = item_seleccionado.text()
        participante_a_mover = None
        for p in self.lista_excepciones:
            if p.nombre == nombre_p:
                participante_a_mover = p
                break
        
        if participante_a_mover:
            # lo mete en la mesa
            mesa_actual.anadirParticipante(participante_a_mover)
            participante_a_mover.asignar_mesa(mesa_actual.id_mesa)
            # lo quita de la lista "conflictos"
            self.lista_excepciones.remove(participante_a_mover) 
            self.actualizar_listas_excepciones_ui()
            self.gestor_datos.guardarEventos(self.lista_eventos) # guarda en json

    # boton "eliminar" (excepciones)
    def excepcion_eliminar_participante(self):
        # pilla el de la lista "en mesa"
        item_seleccionado = self.pagina_excepciones.ui.List_TableParticipants.currentItem()
        if not item_seleccionado or not self.evento_en_edicion_actual:
            return

        mesa_actual = self.evento_en_edicion_actual.mesas[self.excepcion_mesa_actual_idx]
        
        nombre_p = item_seleccionado.text()
        participante_a_mover = None
        for p in mesa_actual.participantes:
            if p.nombre == nombre_p:
                participante_a_mover = p
                break

        if participante_a_mover:
            # lo saca de la mesa
            mesa_actual.eliminarParticipante(participante_a_mover)
            participante_a_mover.quitar_mesa()
            # lo devuelve a la lista "conflictos"
            self.lista_excepciones.append(participante_a_mover) 
            self.actualizar_listas_excepciones_ui()
            self.gestor_datos.guardarEventos(self.lista_eventos) # guarda en json

    # funciones para los botones de csv
    
    # boton "abrir ruta de csv"
    def abrir_carpeta_csvs(self):
        # crea la carpeta si no existe
        os.makedirs(self.CSV_EXPORT_PATH, exist_ok=True)
        
        # la abre
        try:
            webbrowser.open(os.path.realpath(self.CSV_EXPORT_PATH))
            # mensaje de exito
            QMessageBox.information(self, "Carpeta Abierta",
                                  f"Se ha abierto la carpeta:\n{os.path.realpath(self.CSV_EXPORT_PATH)}")
        except Exception as e:
            # mensaje de error
            QMessageBox.critical(self, "Error", f"No se pudo abrir la carpeta.\nError: {e}")

    # boton "generar csv"
    def generar_csv_evento_seleccionado(self):
        # pilla el evento seleccionado
        tabla_crud = self.pagina_crud.ui.EventList_Table
        fila_seleccionada = tabla_crud.currentRow()

        # si no ha elegido evento, avisamos
        if fila_seleccionada == -1:
            QMessageBox.warning(self, "Error", "Selecciona un evento para generar el CSV.")
            return

        try:
            evento_seleccionado = self.lista_eventos[fila_seleccionada]
        except IndexError:
            # si da error, avisamos
            QMessageBox.critical(self, "Error", "Error al obtener el evento.")
            return

        # 1. crea la carpeta si no existe
        os.makedirs(self.CSV_EXPORT_PATH, exist_ok=True)
        
        # 2. limpia el nombre del archivo
        nombre_base = "".join(c for c in evento_seleccionado.nombre if c.isalnum() or c in (' ', '_')).rstrip()
        nombre_archivo = f"{nombre_base.replace(' ', '_')}_completo.csv"
        filePath = os.path.join(self.CSV_EXPORT_PATH, nombre_archivo)

        try:
            # 3. abre el archivo para escribir
            with open(filePath, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                
                # escribe los datos del evento
                writer.writerow(["--- INFORMACION DEL EVENTO ---"])
                writer.writerow(["ID Evento", evento_seleccionado.IdEvento])
                writer.writerow(["Nombre", evento_seleccionado.nombre])
                writer.writerow(["Fecha", evento_seleccionado.fecha])
                writer.writerow(["Ubicacion", evento_seleccionado.ubicacion])
                writer.writerow(["Organizador", evento_seleccionado.organizador])
                writer.writerow(["", ""]) # linea en blanco
                
                # escribe los invitados
                writer.writerow(["--- LISTA DE PARTICIPANTES ---"])
                writer.writerow(["Nombre", "ID Participante", "Preferencias (Nombres)", "Evitados (Nombres)", "Mesa Asignada (ID)"])
                for p in evento_seleccionado.participantes:
                    preferencias_str = "; ".join(p.preferencias)
                    evitados_str = "; ".join(p.evitados)
                    
                    # busca el numero de la mesa
                    nombre_mesa = "Sin Asignar"
                    if p.mesa_asignada:
                        for m in evento_seleccionado.mesas:
                            if m.id_mesa == p.mesa_asignada:
                                nombre_mesa = f"Mesa {m.numero}"
                                break
                                
                    writer.writerow([p.nombre, p.id_participante, preferencias_str, evitados_str, nombre_mesa])
                writer.writerow(["", ""]) # linea en blanco

                # escribe las mesas
                writer.writerow(["--- ASIGNACION DE MESAS ---"])
                for m in evento_seleccionado.mesas:
                    writer.writerow([f"Mesa {m.numero}", f"ID: {m.id_mesa}", f"Capacidad: ({len(m.participantes)} / {m.capacidad})"])
                    
                    # escribe los nombres en esa mesa
                    nombres_en_mesa = [p.nombre for p in m.participantes]
                    if nombres_en_mesa:
                        writer.writerow([""] + nombres_en_mesa) 
                    else:
                        # si no hay nadie
                        writer.writerow(["", "(Mesa Vacia)"])
                    writer.writerow(["", ""]) # linea en blanco
            
            # avisa de que todo ok
            QMessageBox.information(self, "Exito", f"CSV completo generado exitosamente en:\n{os.path.realpath(filePath)}")

        except Exception as e:
            # avisa si hay error
            QMessageBox.critical(self, "Error al escribir CSV", f"No se pudo guardar el archivo.\nError: {e}")


# aqui empieza el programa
if __name__ == "__main__":
    # crea la app
    app = QApplication(sys.argv)
    # crea la ventana
    ventana = VentanaPrincipal()
    # la enseña
    ventana.show()
    # la mantiene abierta
    sys.exit(app.exec_())