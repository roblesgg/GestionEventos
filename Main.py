import sys
from PyQt5.QtWidgets import QApplication, QWidget, QStackedWidget, QMessageBox, QTableWidgetItem, QFileDialog

import csv
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from ortools.sat.python import cp_model
import random

#Importa las vistas
from controllers.CrudEvento import Ui_MainWindow
from controllers.ControllerCrearEvento1 import Ui_Form as Ui_CrearEventoForm
from controllers.ControllerAsignarMesas import Ui_Form as Ui_PaginaMesas
from controllers.EditarEvento import Ui_Form as Ui_ActualizarEventoForm
from controllers.ControllerAsignarMesasManual import Ui_Form as Ui_AsignarManual
from controllers.ControllerBorrarEvento import Ui_DialogoBorrarEvento as Ui_Borrar
from controllers.ControllerAsignarMesasAutomatico import Ui_Form as Ui_ResultadosAuto
from controllers.ControllerAsignarMesasExcepciones import Ui_Form as Ui_Excepciones

from controllers.ControllerCrearEvento2 import Ui_DialogoParticipantes

#importa las clases
from clases.GestorDatos import GestorDatos
from clases.Evento import Evento
from clases.Participante import Participante
from clases.Mesa import Mesa


#Clases de paginas
class PaginaCrud(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

class PaginaCrearEvento(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_CrearEventoForm()
        self.ui.setupUi(self)

class PaginaMesas(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_PaginaMesas()
        self.ui.setupUi(self)
        
class PaginaActualizarEvento(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ActualizarEventoForm()
        self.ui.setupUi(self)

class Manual(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_AsignarManual()
        self.ui.setupUi(self)  

class PaginaBorrar(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Borrar()
        self.ui.setupUi(self)

class PaginaGestionarParticipantes(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_DialogoParticipantes()
        self.ui.setupUi(self)

class PaginaMesasAutomatico(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ResultadosAuto()
        self.ui.setupUi(self)

class PaginaExcepciones(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Excepciones()
        self.ui.setupUi(self)

#Ventana principal
class VentanaPrincipal(QStackedWidget):
    def __init__(self):
        super().__init__()
        
        #el json bd
        self.gestor_datos = GestorDatos("eventos.json") 
        #para guardar todos los eventoss
        self.lista_eventos = []
        #para guardar los dtos del evento seleccionado en la tabla
        self.evento_en_edicion_actual = None
        #para guardar las excepciones
        self.lista_excepciones = []

        # --- MODIFICADO: Variables de estado ---
        self.modo_gestion_participantes = None # --- NUEVO: Puede ser "CREAR" o "ACTUALIZAR" ---
        self.participante_en_gestion = None # Para la página 6
        self.mesa_manual_actual_idx = 0     # Para la página 4
        self.excepcion_mesa_actual_idx = 0  # Para la página 8
        # --- FIN MODIFICADO ---


        #Las paginas
        self.pagina_crud = PaginaCrud()           #0
        self.pagina_crear = PaginaCrearEvento()     #1
        self.pagina_actualizar = PaginaActualizarEvento() #2
        self.pagina_mesas = PaginaMesas()         #3
        self.pagina_manual=Manual()             #4
        self.pagina_borrar=PaginaBorrar()       #5
        self.pagina_participantes = PaginaGestionarParticipantes() #6
        self.pagina_resultados_auto = PaginaMesasAutomatico() #7
        self.pagina_excepciones = PaginaExcepciones() #8
        
        #añade las paginas
        self.addWidget(self.pagina_crud)           #0
        self.addWidget(self.pagina_crear)         #1
        self.addWidget(self.pagina_actualizar)    #2
        self.addWidget(self.pagina_mesas)          #3
        self.addWidget(self.pagina_manual)          #4
        self.addWidget(self.pagina_borrar)         #5
        self.addWidget(self.pagina_participantes)  #6
        self.addWidget(self.pagina_resultados_auto) #7
        self.addWidget(self.pagina_excepciones) #8

        #Conecta los botones
        #botones del crud 0
        self.pagina_crud.ui.CreateEvent_Btn.clicked.connect(self.mostrar_pagina_crear)
        self.pagina_crud.ui.UpdateEvent_Btn.clicked.connect(self.mostrar_pagina_actualizar)
        self.pagina_crud.ui.AssignTables_Btn.clicked.connect(self.mostrar_pagina_mesas)
        self.pagina_crud.ui.DeleteEvent_Btn.clicked.connect(self.mostrar_pagina_borrar)
        
        # --- MODIFICADO: Conexión para el algoritmo (reemplaza la línea antigua) ---
        self.pagina_mesas.ui.AutoAssign_Btn.clicked.connect(self.ejecutar_asignacion_automatica)
        # --- FIN MODIFICADO ---
        
        self.pagina_resultados_auto.ui.ViewExceptions_Btn.clicked.connect(self.mostrar_pagina_excepciones)

        #botones de otras pestañas
        self.pagina_mesas.ui.ManualAssign_Btn.clicked.connect(self.mostrar_pagina_manual)
        self.pagina_crear.ui.CreateManual_Btn.clicked.connect(self.preparar_evento_para_participantes)
        self.pagina_crud.ui.OpenCSVPath_Btn.clicked.connect(self.seleccionar_csv)
        self.pagina_crear.ui.UploadCSV_Btn.clicked.connect(self.cargar_participantes_csv)
        self.pagina_actualizar.ui.UploadCSV_Btn.clicked.connect(self.cargar_participantes_csv)

        # --- NUEVO: Conexión para "Añadir Manualmente" en la página de Actualizar Evento ---
        self.pagina_actualizar.ui.CreateManual_Btn.clicked.connect(self.mostrar_pagina_participantes_actualizar)
        # --- FIN NUEVO ---

        #mas botones
        #boton atras 1
        self.pagina_crear.ui.BackButton_CreateEvent.clicked.connect(self.mostrar_pagina_crud)

        #boton finalizar
        self.pagina_crear.ui.FinishCreateEvent_Btn.clicked.connect(self.guardar_nuevo_evento)
        
        #atras de actualizar evento 2
        self.pagina_actualizar.ui.BackButton_UpdateEvent.clicked.connect(self.mostrar_pagina_crud)
        
        #atras de asignar mesas 3
        self.pagina_mesas.ui.BackButton_AssignMenu.clicked.connect(self.mostrar_pagina_crud)

        #atras de borrar 5
        self.pagina_borrar.ui.BackButton_DeleteEvent.clicked.connect(self.mostrar_pagina_crud)

        #Borra el evento 
        self.pagina_borrar.ui.ConfirmDelete_Btn.clicked.connect(self.borrar_evento_seleccionado)

        #Actualiza el evento 
        self.pagina_actualizar.ui.SaveUpdate_Btn.clicked.connect(self.guardar_evento_actualizado)
        
        # --- MODIFICADO: Conexiones para la PÁGINA 6 (Gestionar Participantes) ---
        # El botón de atrás se conectará dinámicamente
        self.pagina_participantes.ui.Add_Btn.clicked.connect(self.anadir_participante_al_evento)
        # El botón de finalizar se conectará dinámicamente
        
        # --- MODIFICADO: Un SOLO clic ya no carga. Se usa DOBLE CLIC para cargar. ---
        self.pagina_participantes.ui.List_AllGuests.itemDoubleClicked.connect(self.gestionar_participante_seleccionado)
        
        # Si el usuario escribe en el campo de texto, significa que quiere crear uno NUEVO
        self.pagina_participantes.ui.Input_ParticipantName.textChanged.connect(self.limpiar_participante_en_gestion)

        # Botones V, X y Eliminar
        self.pagina_participantes.ui.MoveToPreference_Btn.clicked.connect(self.participante_anadir_preferencia)
        self.pagina_participantes.ui.MoveToAvoid_Btn.clicked.connect(self.participante_anadir_evitado)
        self.pagina_participantes.ui.RemoveFromList_Btn.clicked.connect(self.participante_eliminar_relacion)
        # --- FIN MODIFICADO ---

        # Botón atrás de añadir
        self.pagina_manual.ui.BackButton_ManualAssign.clicked.connect(self.mostrar_pagina_mesas)

        # --- NUEVO: Conexiones para la PÁGINA 4 (Asignación Manual) ---
        self.pagina_manual.ui.NextTable_Btn.clicked.connect(self.manual_siguiente_mesa)
        self.pagina_manual.ui.PrevTable_Btn.clicked.connect(self.manual_anterior_mesa)
        self.pagina_manual.ui.AddParticipant_Btn.clicked.connect(self.manual_anadir_participante)
        self.pagina_manual.ui.RemoveParticipant_Btn.clicked.connect(self.manual_eliminar_participante)
        # --- FIN NUEVO ---

        # Botón atrás de automático 
        self.pagina_resultados_auto.ui.BackButton_AutoAssign.clicked.connect(self.mostrar_pagina_mesas)

        # Botón atrás excepciones
        self.pagina_excepciones.ui.BackButton_Exceptions.clicked.connect(self.mostrar_pagina_auto)
        
        # --- NUEVO: Conexiones para la PÁGINA 8 (Excepciones) ---
        self.pagina_excepciones.ui.NextTable_Btn.clicked.connect(self.excepcion_siguiente_mesa)
        self.pagina_excepciones.ui.PrevTable_Btn.clicked.connect(self.excepcion_anterior_mesa)
        self.pagina_excepciones.ui.AddParticipant_Btn.clicked.connect(self.excepcion_anadir_participante)
        self.pagina_excepciones.ui.RemoveParticipant_Btn.clicked.connect(self.excepcion_eliminar_participante)
        # --- FIN NUEVO ---
        
        # --- NUEVO: Conexión para el botón de Generar CSV ---
        self.pagina_crud.ui.GenerateCSV_Btn.clicked.connect(self.generar_csv_evento_seleccionado)
        # --- FIN NUEVO ---
        
        #la pestaña inicial
        self.resize(904, 617)
        #pone los eventos del csv
        self.cargar_y_actualizar_eventos()


    #metodos de cambiar de pagina
    def mostrar_pagina_crud(self):
        self.actualizar_tabla_crud()
        self.setCurrentIndex(0)
        
    def mostrar_pagina_crear(self):
        # --- MODIFICADO: Limpiar el evento en edición al ir a la pág. de crear ---
        self.evento_en_edicion_actual = None
        self.participante_en_gestion = None
        self.pagina_participantes.ui.Input_ParticipantName.setText("") # Limpia el campo
        self.actualizar_listas_participantes() # Limpia todas las listas
        # --- FIN MODIFICADO ---
        self.setCurrentIndex(1) 

    def mostrar_pagina_actualizar(self):
        #guarda la tabla
        tabla_crud = self.pagina_crud.ui.EventList_Table
        
        #guarda el evento seleccionado en la tabla
        fila_seleccionada = tabla_crud.currentRow()

        #comprueba que no haya nada seleccionado
        if fila_seleccionada == -1:
            QMessageBox.warning(self, "Error", "Selecciona un evento para editar")
            return #para que se salga

        #coge el evento que ha en la fila
        try:
            #guarda el evento en esta variable
            self.evento_en_edicion_actual = self.lista_eventos[fila_seleccionada]
            # --- MODIFICADO: Limpiar el participante en gestión ---
            self.participante_en_gestion = None
            self.pagina_participantes.ui.Input_ParticipantName.setText("") # Limpia el campo
            self.actualizar_listas_participantes() # Limpia todas las listas
            # --- FIN MODIFICADO ---
        except IndexError:
            QMessageBox.critical(self, "Error")
            return

        #rellena los campos de actualizar con los del evento
        self.pagina_actualizar.ui.Input_EventName.setText(self.evento_en_edicion_actual.nombre)
        self.pagina_actualizar.ui.Input_EventDate.setText(self.evento_en_edicion_actual.fecha)
        self.pagina_actualizar.ui.Input_EventLocation.setText(self.evento_en_edicion_actual.ubicacion)
        self.pagina_actualizar.ui.Input_EventOrganizer.setText(self.evento_en_edicion_actual.organizador)
        self.pagina_actualizar.ui.Input_NumTables.setValue(self.evento_en_edicion_actual.numMesas)
        
        #pone la pagina
        self.setCurrentIndex(2)

    def mostrar_pagina_mesas(self):

        # Guarda la tabla en la variable 
        tabla_crud = self.pagina_crud.ui.EventList_Table
        # Toma la fila seleccionada
        fila_seleccionada = tabla_crud.currentRow()

        # Comprueba que haya alguna fila seleccionada
        if fila_seleccionada == -1:
            QMessageBox.warning(self, "Sin selección", "Por favor, selecciona un evento para asignar sus mesas.")
            return

        # Declara la fila seleccionada como evento_en_edicion_actual
        try:
            self.evento_en_edicion_actual = self.lista_eventos[fila_seleccionada]
            print(f"Gestionando mesas para el evento: {self.evento_en_edicion_actual.nombre}")
        except IndexError:
            QMessageBox.critical(self, "Error")
            return # Sale del método

        # 4. Abre la página asignar mesas
        self.setCurrentIndex(3)

    # --- NUEVO: Función modificada para gestionar la Pág. 4 ---
    def mostrar_pagina_manual(self):
        """ Sobreescribe la función para inicializar las listas. """
        if self.evento_en_edicion_actual is None:
            QMessageBox.warning(self, "Error", "No hay evento seleccionado.")
            return
            
        self.mesa_manual_actual_idx = 0 # Reinicia al ver la página
        self.actualizar_listas_manual()
        self.setCurrentIndex(4)
    # --- FIN NUEVO ---

    def mostrar_pagina_borrar(self):
        self.setCurrentIndex(5)
        self.cargar_y_actualizar_eventos_borrar()
    


    #mas metodos varios

    def preparar_evento_para_participantes(self):
        
        # --- MODIFICADO: Lógica para manejar la creación de un evento temporal ---
        # Si el evento en edición no existe, crea uno temporal
        if self.evento_en_edicion_actual is None:
            if not self._crear_evento_temporal_desde_pagina1():
                return # Si falla (ej: falta nombre/fecha), no continúa
        # --- FIN MODIFICADO ---

        # 6. Actualiza las listas de la Pág 6 y muéstrala
        self.actualizar_listas_participantes()
        
        # --- MODIFICADO: Conectar botones de Pág. 6 para el flujo de "CREAR" ---
        self.modo_gestion_participantes = "CREAR" # --- NUEVO: Usar la variable de estado ---
        try:
            # Desconecta conexiones anteriores para evitar duplicados
            self.pagina_participantes.ui.BackButton_Participants.clicked.disconnect()
            self.pagina_participantes.ui.Finish_Btn.clicked.disconnect()
        except TypeError:
            pass # No pasa nada si no estaban conectadas
            
        # Conecta "Atrás" para que vuelva a "Crear Evento" (Pág. 1)
        self.pagina_participantes.ui.BackButton_Participants.clicked.connect(self.mostrar_pagina_crear)
        # Conecta "Finalizar" para que guarde el *nuevo* evento
        self.pagina_participantes.ui.Finish_Btn.clicked.connect(self.guardar_evento_y_participantes)
        # --- FIN MODIFICADO ---
        
        self.setCurrentIndex(6) # Ir a la página 6

    # --- NUEVO: Función para manejar "Añadir Manualmente" desde "Actualizar Evento" ---
    def mostrar_pagina_participantes_actualizar(self):
        """
        Se llama desde el botón 'Crear participantes manualmente' de la PÁGINA DE ACTUALIZAR (Página 2).
        """
        if self.evento_en_edicion_actual is None:
            QMessageBox.critical(self, "Error", "No hay ningún evento seleccionado. Esto no debería pasar.")
            return

        # El evento ya está cargado en self.evento_en_edicion_actual
        # Actualizamos las listas de la UI con los datos de este evento
        self.actualizar_listas_participantes()
        
        # --- MODIFICADO: Conectar botones de Pág. 6 para el flujo de "ACTUALIZAR" ---
        self.modo_gestion_participantes = "ACTUALIZAR" # --- NUEVO: Usar la variable de estado ---
        try:
            # Desconecta conexiones anteriores
            self.pagina_participantes.ui.BackButton_Participants.clicked.disconnect()
            self.pagina_participantes.ui.Finish_Btn.clicked.disconnect()
        except TypeError:
            pass # No pasa nada
            
        # Conecta "Atrás" para que vuelva a "Actualizar Evento" (Pág. 2)
        self.pagina_participantes.ui.BackButton_Participants.clicked.connect(self.mostrar_pagina_actualizar)
        # Conecta "Finalizar" para que *solo* vuelva a "Actualizar Evento" (Pág. 2)
        # NO guarda nada aquí. El guardado se hace en la Pág. 2 con el botón "Guardar Cambios".
        self.pagina_participantes.ui.Finish_Btn.clicked.connect(self.mostrar_pagina_actualizar)
        # --- FIN MODIFICADO ---
        
        self.setCurrentIndex(6) # Ir a la página 6
    # --- FIN NUEVO ---

    # --- MODIFICADO: Lógica de "Añadir" adaptada al nuevo flujo ---
    def anadir_participante_al_evento(self):
        """
        Añade un participante desde el campo de texto superior.
        Lo añade al evento y lo selecciona para editar sus preferencias.
        """
        # 1. Comprobar si tenemos un evento (temporal o real)
        if self.evento_en_edicion_actual is None:
             if not self._crear_evento_temporal_desde_pagina1():
                return # Si falla (ej: falta nombre/fecha), no continúa
        
        # 2. Obtener nombre y validar
        nombre_participante = self.pagina_participantes.ui.Input_ParticipantName.text().strip()
        if not nombre_participante:
            QMessageBox.warning(self, "Oye", "Escribe el nombre del participante.")
            return
            
        # 3. Comprobar si ya existe
        for p in self.evento_en_edicion_actual.participantes:
            if p.nombre.lower() == nombre_participante.lower():
                QMessageBox.warning(self, "Duplicado", f"El participante '{nombre_participante}' ya existe en este evento.")
                return

        # 4. Crear y añadir
        evento_id = self.evento_en_edicion_actual.IdEvento
        num_part = len(self.evento_en_edicion_actual.participantes)
        participante_id = f"{evento_id}_p_{num_part + 1}"

        nuevo_participante = Participante(participante_id, nombre_participante)
        self.evento_en_edicion_actual.anadirparticipante(nuevo_participante)
        
        # 5. Seleccionar al nuevo participante para editarlo
        self.participante_en_gestion = nuevo_participante
        
        # 6. Refrescar listas
        self.actualizar_listas_participantes()
        
        # 7. Resaltar al nuevo participante en la lista
        for i in range(self.pagina_participantes.ui.List_AllGuests.count()):
            item = self.pagina_participantes.ui.List_AllGuests.item(i)
            if item.text() == nombre_participante:
                item.setSelected(True)
                # --- NUEVO: Cargar sus (vacías) preferencias ---
                self.actualizar_listas_preferencias()
                # --- FIN NUEVO ---
                break
        
        # --- MODIFICADO: Corregir el 'TypeError' ---
        # 8. Guardar cambios si estamos en "Actualizar"
        if self.modo_gestion_participantes == "ACTUALIZAR":
            self.gestor_datos.guardarEventos(self.lista_eventos)
        # --- FIN MODIFICADO ---
    # --- FIN MODIFICADO ---

    def actualizar_listas_participantes(self):
        """
        Actualiza la lista "Todos los Invitados".
        Limpia las listas de preferencias/evitados.
        """
        lista_invitados = self.pagina_participantes.ui.List_AllGuests
        lista_pref = self.pagina_participantes.ui.List_Preference
        lista_no = self.pagina_participantes.ui.List_Avoid
        
        lista_invitados.clear()
        lista_pref.clear()
        lista_no.clear()

        # Rellenar lista "Todos los Invitados"
        if self.evento_en_edicion_actual:
            for participante in self.evento_en_edicion_actual.participantes:
                lista_invitados.addItem(participante.nombre)
        
        # --- MODIFICADO: Limpiar selección ---
        self.pagina_participantes.ui.List_AllGuests.clearSelection()
        # No limpiamos el 'participante_en_gestion' aquí
        # --- FIN MODIFICADO ---
        
    def guardar_evento_y_participantes(self):
        """
        Se llama SOLO desde el flujo de "Crear Evento".
        Guarda el evento temporal (con sus participantes) en la lista principal y en el JSON.
        """
        if self.evento_en_edicion_actual is None:
            QMessageBox.critical(self, "Error", "No hay evento que guardar.")
            return
            
        # --- MODIFICADO: Comprobar si el evento ya existe (flujo de actualizar) ---
        evento_existe = False
        for ev in self.lista_eventos:
            if ev.IdEvento == self.evento_en_edicion_actual.IdEvento:
                evento_existe = True
                break
        
        if not evento_existe:
             self.lista_eventos.append(self.evento_en_edicion_actual)
        # --- FIN MODIFICADO ---
        
        #Guarda en el json
        self.gestor_datos.guardarEventos(self.lista_eventos)

        #vacia el aux
        self.evento_en_edicion_actual = None
        self.participante_en_gestion = None # --- NUEVO ---
        
        #vacia todos los txt
        self.pagina_crear.ui.Input_EventName.setText("")
        self.pagina_crear.ui.Input_EventDate.setText("")
        self.pagina_crear.ui.Input_EventLocation.setText("")
        self.pagina_crear.ui.Input_EventOrganizer.setText("")
        self.pagina_crear.ui.Input_NumTables.setValue(1)
        
        # --- NUEVO: Limpiar la página de participantes ---
        self.pagina_participantes.ui.Input_ParticipantName.setText("")
        self.actualizar_listas_participantes()
        # --- FIN NUEVO ---

        #vuelve al crud
        self.mostrar_pagina_crud()


#guarda el evento de actualizar evento
    def guardar_evento_actualizado(self):

        #coge los datos de las casillas de actualizar a variables
        nuevo_nombre = self.pagina_actualizar.ui.Input_EventName.text()
        nueva_fecha = self.pagina_actualizar.ui.Input_EventDate.text()
        nueva_ubicacion = self.pagina_actualizar.ui.Input_EventLocation.text()
        nuevo_organizador = self.pagina_actualizar.ui.Input_EventOrganizer.text()
        nuevo_numMesas = self.pagina_actualizar.ui.Input_NumTables.value()

        #comrpueba que nos e queden sin escriobir fecha ni nombre
        if not nuevo_nombre or not nueva_fecha:
            QMessageBox.warning(self,  "Oye", "Pon el nombre y la fecha")       
            return #sale del metodo

        #guarda los nuevos datos en variables
        self.evento_en_edicion_actual.nombre = nuevo_nombre
        self.evento_en_edicion_actual.fecha = nueva_fecha
        self.evento_en_edicion_actual.ubicacion = nueva_ubicacion
        self.evento_en_edicion_actual.organizador = nuevo_organizador

        #comprueba si ha cambiado el numero de mesas
        if self.evento_en_edicion_actual.numMesas != nuevo_numMesas:
            #cambia el num de mesas
            self.evento_en_edicion_actual.numMesas = nuevo_numMesas
            #borra todas las mesas
            self.evento_en_edicion_actual.mesas = []
            capacidad_por_mesa = 10#pone la cappacida por defecto
            #Crea las mesas nuevas vacias tantas como ponga en el nuevo campo
            for i in range(nuevo_numMesas):
                id_mesa = f"{self.evento_en_edicion_actual.IdEvento}_mesa_{i+1}"
                nueva_mesa = Mesa(id_mesa=id_mesa, numero=i+1, capacidad=capacidad_por_mesa)
                self.evento_en_edicion_actual.mesas.append(nueva_mesa)
            QMessageBox.warning(self,"Oye", "Se restauraron las mesas tendras que asignar de nuevo")       

        #Guarda en json
        self.gestor_datos.guardarEventos(self.lista_eventos)
        #vacia el evento en edicion para el proximo
        self.evento_en_edicion_actual = None
        #vuelve al crud
        self.mostrar_pagina_crud()


    def borrar_evento_seleccionado(self):

        #Instancia la tabla borrar
        tabla_borrar = self.pagina_borrar.ui.EventList_Table_Delete
        
        #coge el seleccionado
        fila_seleccionada = tabla_borrar.currentRow()

        #comprueba si no hay nada seleccionado
        if fila_seleccionada == -1:
            # Si no hay nada seleccionado, mostrar un aviso y no hacer nada
            QMessageBox.warning(self, "Oye", "No has seleccionado ningun evento.")
            return#para que no haga nada y salga del metodo

        #Coge el seleccionado
        try:
            evento_a_borrar = self.lista_eventos[fila_seleccionada]
            nombre_evento = evento_a_borrar.nombre
        except IndexError:
            QMessageBox.critical(self, "Error", "no se ha podido borrar")
            return

        # la confirmacion
        confirmacion = QMessageBox.question(
            self,
            "Confirmar borrado",
            f"¿Estás seguro de que quieres borrar el evento '{nombre_evento}'?\n\nEsta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No#no por defecto
        )

        #si ha dicho que si
        if confirmacion == QMessageBox.Yes:
            #Borra de la lista
            self.lista_eventos.pop(fila_seleccionada)
            
            #Guarda en el json
            self.gestor_datos.guardarEventos(self.lista_eventos)
            
            #refresca
            self.actualizar_tabla_borrar()

            #vuelve al menu
            self.mostrar_pagina_crud()
            
        else:
            #no hace nada
            return

    def cargar_y_actualizar_eventos(self):
        self.lista_eventos = self.gestor_datos.cargarEventos()
        self.actualizar_tabla_crud()

    def cargar_y_actualizar_eventos_borrar(self):
        self.lista_eventos = self.gestor_datos.cargarEventos()
        self.actualizar_tabla_borrar()

#METODO DE CREAR EL EVENTO SUPER TOCHO real no fake 100€
    def guardar_nuevo_evento(self):
        #coge los datos de la pag 1 crear evento
        nombre = self.pagina_crear.ui.Input_EventName.text()
        fecha = self.pagina_crear.ui.Input_EventDate.text()
        ubicacion = self.pagina_crear.ui.Input_EventLocation.text()
        organizador = self.pagina_crear.ui.Input_EventOrganizer.text()
        numMesas = self.pagina_crear.ui.Input_NumTables.value()

        #comprueba que no falten nombre nii fecha
        if not nombre or not fecha:
            QMessageBox.warning(self,  "Oye", "Pon el nombre y la fecha")       
            return#estoi es para que salga
            
        # --- MODIFICADO: Si se creó un evento temporal, lo usamos en lugar de crear uno nuevo ---
        if self.evento_en_edicion_actual and self.evento_en_edicion_actual.nombre == nombre:
            nuevo_evento = self.evento_en_edicion_actual
            # Actualizamos por si acaso cambiaron algo después de cargar el CSV
            nuevo_evento.fecha = fecha
            nuevo_evento.ubicacion = ubicacion
            nuevo_evento.organizador = organizador
            nuevo_evento.numMesas = numMesas
        else:
        # --- FIN MODIFICADO ---
            #crea el id
            nuevo_id = f"evento_{len(self.lista_eventos) + 1}"

            #crea el evento
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

        #Añade el evento a la lista de eventos
        self.lista_eventos.append(nuevo_evento)

        #Guarda la lista
        self.gestor_datos.guardarEventos(self.lista_eventos)


        #vacia los text field
        self.pagina_crear.ui.Input_EventName.setText("")
        self.pagina_crear.ui.Input_EventDate.setText("")
        self.pagina_crear.ui.Input_EventLocation.setText("")
        self.pagina_crear.ui.Input_EventOrganizer.setText("")
        self.pagina_crear.ui.Input_NumTables.setValue(1)
        
        # --- MODIFICADO: Limpiar variables de estado ---
        self.evento_en_edicion_actual = None
        self.participante_en_gestion = None
        self.pagina_participantes.ui.Input_ParticipantName.setText("")
        self.actualizar_listas_participantes()
        # --- FIN MODIFICADO ---

        #para acabar vuelve a la pagina principal
        self.mostrar_pagina_crud()

    def actualizar_tabla_crud(self):

        #la tabla
        tabla = self.pagina_crud.ui.EventList_Table
        
        #para latabla para que nos e raye
        tabla.blockSignals(True)
        
        #limpia la tabla
        tabla.setRowCount(0) 
        
        # recorre los eventos
        for evento in self.lista_eventos:
            #coge la posicion
            row_position = tabla.rowCount()
            #mete una fila
            tabla.insertRow(row_position)
            
            #añade las columnas
            tabla.setItem(row_position, 0, QTableWidgetItem(evento.nombre))
            tabla.setItem(row_position, 1, QTableWidgetItem(evento.fecha))
            tabla.setItem(row_position, 2, QTableWidgetItem(evento.ubicacion))
            tabla.setItem(row_position, 3, QTableWidgetItem(evento.organizador))
            
        #activa de vuelta la tabla
        tabla.blockSignals(False)
        
        tabla.resizeColumnsToContents()

    def actualizar_tabla_borrar(self): # --- MODIFICADO: He quitado 'ruta' de los parámetros, no se usaba ---
        tabla = self.pagina_borrar.ui.EventList_Table_Delete
        tabla.blockSignals(True)
        tabla.setRowCount(0)
         #recorre los eventos
        for evento in self.lista_eventos:
            # coge la posicion
            row_position = tabla.rowCount()
            # mete una fila
            tabla.insertRow(row_position)

            # añade las columnas
            tabla.setItem(row_position, 0, QTableWidgetItem(evento.nombre))
            tabla.setItem(row_position, 1, QTableWidgetItem(evento.fecha))
            tabla.setItem(row_position, 2, QTableWidgetItem(evento.ubicacion))
            tabla.setItem(row_position, 3, QTableWidgetItem(evento.organizador))
            
        tabla.blockSignals(False) # --- NUEVO: Faltaba esta línea ---

    def Crear_SubirCSV(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Selecciona un archivo CSV", "", "Archivos CSV (*.csv)")
        if archivo:
            try:
                # --- MODIFICADO: 'pd' no está definido, esto daría error. Lo comento. ---
                # df = pd.read_csv(archivo) 
                # print("Archivo cargado con éxito:")
                # print(df.head())
                
                # # Ejemplo: agregar participantes desde CSV
                # if self.evento_en_edicion_actual:
                #     for nombre in df.iloc[:,0]:  # asume que la primera columna tiene los nombres
                #         participante_id = f"{self.evento_en_edicion_actual.IdEvento}_p_{len(self.evento_en_edicion_actual.participantes) + 1}"
                #         nuevo_participante = Participante(participante_id, nombre)
                #         self.evento_en_edicion_actual.anadirparticipante(nuevo_participante)
                    
                #     self.actualizar_listas_participantes()  # refresca lista en interfaz
                #     QMessageBox.information(self, "Éxito", "Participantes importados desde CSV")
                # --- FIN MODIFICADO ---
                pass # No hace nada por ahora
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo leer el CSV:\n{str(e)}")
        else:
            QMessageBox.warning(self, "Cancelado", "No se seleccionó ningún archivo")

    def seleccionar_csv(self,ruta):
        ruta, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo CSV", "", "CSV Files (*.csv)")
        # --- MODIFICADO: La siguiente línea no tiene sentido aquí, la comento ---
        # self.actualizar_tabla_crud(ruta) 
        # --- FIN MODIFICADO ---
        if ruta:
             # --- MODIFICADO: 'pd' no está definido, esto daría error. Lo comento. ---
            # self.cargar_csv(ruta)
            pass
    
    def cargar_csv(self, ruta):
        # --- MODIFICADO: 'pd' no está definido, esto daría error. Lo comento. ---
        # df = pd.read_csv(ruta)
        # self.tabla.setRowCount(len(df))
        # self.tabla.setColumnCount(len(df.columns))
        # self.tabla.setHorizontalHeaderLabels(df.columns)

        # for i in range(len(df)):
        #     for j in range(len(df.columns)):
        #         self.tabla.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))
        # --- FIN MODIFICADO ---
        pass

    def mostrar_pagina_auto(self):
        self.setCurrentIndex(7)

    # --- NUEVO: Función modificada para gestionar la Pág. 8 ---
    def mostrar_pagina_excepciones(self):
        """ Sobreescribe la función para inicializar las listas. """
        if self.evento_en_edicion_actual is None:
            return
            
        self.excepcion_mesa_actual_idx = 0 # Reinicia al ver la página
        self.actualizar_listas_excepciones_ui()
        self.setCurrentIndex(8)
    # --- FIN NUEVO ---

    # --- NUEVO: Algoritmo OR-Tools (reemplaza al anterior) ---
    def algoritmo_asignar_mesas(self, participantes, mesas):
        """
        Algoritmo de asignación automática usando Google OR-Tools.
        Intenta satisfacer las restricciones de preferencias y evitados.
        """
        
        # 0. Comprobaciones iniciales
        excepciones = []
        if not mesas:
            print("Error: No hay mesas para asignar.")
            return participantes  # Todos son excepciones si no hay mesas
        
        if not participantes:
            print("No hay participantes para asignar.")
            return [] # No hay excepciones

        # 1. Mapeos de nombres y IDs
        # Necesarios para que el modelo pueda relacionar nombres (de preferencias) con IDs (de variables)
        nombre_a_obj = {p.nombre: p for p in participantes}
        
        # 2. Crear el Modelo
        model = cp_model.CpModel()

        # 3. Crear Variables
        # Para cada participante, su variable guardará el ÍNDICE (0, 1, 2...) de la mesa asignada.
        participante_vars = {
            p.id_participante: model.NewIntVar(0, len(mesas) - 1, p.nombre)
            for p in participantes
        }

        # 4. Añadir Restricciones

        # 4a. Restricción de Capacidad de Mesa
        for i, mesa in enumerate(mesas):
            # Contamos cuántos participantes tienen su variable asignada al índice 'i'
            indicadores = []
            for p in participantes:
                p_id = p.id_participante
                # b es True si participante_vars[p_id] == i
                b = model.NewBoolVar(f"{p_id}_en_mesa_{i}")
                model.Add(participante_vars[p_id] == i).OnlyEnforceIf(b)
                model.Add(participante_vars[p_id] != i).OnlyEnforceIf(b.Not())
                indicadores.append(b)
            
            # La suma de indicadores (participantes en la mesa) no debe superar la capacidad
            model.Add(sum(indicadores) <= mesa.capacidad)

        # 4b. Restricción de Preferencias (Amigos)
        # Usamos un set para no añadir la misma restricción dos veces (Ana-Luis, Luis-Ana)
        preferencias_procesadas = set()
        for p in participantes:
            var_p = participante_vars[p.id_participante]
            for amigo_nombre in p.preferencias:
                
                # Si el amigo existe en la lista de participantes Y aún no hemos procesado este par
                if amigo_nombre in nombre_a_obj and (amigo_nombre, p.nombre) not in preferencias_procesadas:
                    amigo_obj = nombre_a_obj[amigo_nombre]
                    var_amigo = participante_vars[amigo_obj.id_participante]
                    
                    # Forzar a que sus variables de mesa sean iguales
                    model.Add(var_p == var_amigo)
                    preferencias_procesadas.add((p.nombre, amigo_nombre))

        # 4c. Restricción de Evitados (Enemigos)
        for p in participantes:
            var_p = participante_vars[p.id_participante]
            for enemigo_nombre in p.evitados:
                
                if enemigo_nombre in nombre_a_obj:
                    enemigo_obj = nombre_a_obj[enemigo_nombre]
                    var_enemigo = participante_vars[enemigo_obj.id_participante]
                    
                    # Forzar a que sus variables de mesa sean DIFERENTES
                    model.Add(var_p != var_enemigo)

        # 5. Resolver el Modelo
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        # 6. Procesar Resultados
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print("Asignación automática completada (OR-Tools).")
            
            # Asignar participantes a las mesas (en los objetos)
            for p in participantes:
                id_mesa_asignada = solver.Value(participante_vars[p.id_participante])
                mesa_obj = mesas[id_mesa_asignada]
                
                # Añadimos al objeto Mesa y actualizamos el objeto Participante
                mesa_obj.anadirParticipante(p)
                p.asignar_mesa(mesa_obj.id_mesa)
            
            # Si el modelo tuvo éxito, no hay excepciones
            return [] 
            
        else:
            # Si el modelo es INFACTIBLE (no se puede cumplir todo)
            print("No se encontró solución factible con OR-Tools.")
            QMessageBox.warning(self, "Conflicto de Asignación", 
                                "No se pudo encontrar una solución que respete todas las reglas (preferencias/evitados).\n\n"
                                "Revisa las restricciones o usa la asignación manual.")
            
            # Devolvemos todos los participantes como excepciones para resolver manualmente
            return participantes
    # --- FIN NUEVO ---


    def ejecutar_asignacion_automatica(self):
        # Comprobamos que tenemos un evento seleccionado
        if self.evento_en_edicion_actual is None:
            QMessageBox.critical(self, "Error")
            return

        print(f"Iniciando asignación automática para: {self.evento_en_edicion_actual.nombre}")

        # Vacía las mesas
        for mesa in self.evento_en_edicion_actual.mesas:
            mesa.participantes = []

        # Limpia el campo mesas asignadas
        for p in self.evento_en_edicion_actual.participantes:
            p.quitar_mesa()

        # Crea los lists para el algoritmo
        participantes_a_asignar = list(self.evento_en_edicion_actual.participantes)
        mesas_del_evento = list(self.evento_en_edicion_actual.mesas)

        # Llama al método del algoritmo
        self.lista_excepciones = self.algoritmo_asignar_mesas(participantes_a_asignar, mesas_del_evento)

        # Lo guarda en el JSON
        self.gestor_datos.guardarEventos(self.lista_eventos)

        # Actualiza las tablas
        self.actualizar_tabla_resultados_auto()
        self.actualizar_lista_excepciones()

        # Mostrar la página de resultados
        self.mostrar_pagina_auto()


    def actualizar_tabla_resultados_auto(self):
        tabla = self.pagina_resultados_auto.ui.Results_Table
        tabla.blockSignals(True)
        tabla.setRowCount(0)

        if self.evento_en_edicion_actual:
            # Relleno mesa por mesa
            for mesa in self.evento_en_edicion_actual.mesas:
                row_position = tabla.rowCount()
                tabla.insertRow(row_position)

                texto_mesa = f"Mesa {mesa.numero} ({len(mesa.participantes)}/{mesa.capacidad})"
                tabla.setItem(row_position, 0, QTableWidgetItem(texto_mesa))

                nombres = [p.nombre for p in mesa.participantes]
                texto_nombres = ", ".join(nombres)
                tabla.setItem(row_position, 1, QTableWidgetItem(texto_nombres))

        tabla.blockSignals(False)
        # Ajustar el tamaño de las columnas al contenido
        tabla.resizeColumnsToContents()


    def actualizar_lista_excepciones(self):
        lista = self.pagina_excepciones.ui.List_Exceptions
        lista.clear()

        for participante in self.lista_excepciones:
            lista.addItem(participante.nombre)

    # --- NUEVO: Función auxiliar para crear evento temporal ---
    def _crear_evento_temporal_desde_pagina1(self):
        """
        Crea un evento temporal desde los datos de la página 1 (Crear Evento)
        sin guardarlo en la lista ni en JSON.
        Retorna True si se creó correctamente, False si falta información.
        """
        nombre = self.pagina_crear.ui.Input_EventName.text().strip()
        fecha = self.pagina_crear.ui.Input_EventDate.text().strip()
        
        if not nombre or not fecha:
            QMessageBox.warning(self, "Datos incompletos", 
                            "Debes completar al menos el Nombre y la Fecha del evento antes de cargar participantes.")
            return False
        
        ubicacion = self.pagina_crear.ui.Input_EventLocation.text().strip()
        organizador = self.pagina_crear.ui.Input_EventOrganizer.text().strip()
        numMesas = self.pagina_crear.ui.Input_NumTables.value()
        nuevo_id = f"evento_{len(self.lista_eventos) + 1}"
        
        try:
            self.evento_en_edicion_actual = Evento(
                IdEvento=nuevo_id,
                nombre=nombre,
                fecha=fecha,
                ubicacion=ubicacion,
                organizador=organizador,
                numMesas=numMesas
            )
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo crear el evento temporal.\n{e}")
            return False
    # --- FIN NUEVO ---
    
    def cargar_participantes_csv(self):
        """
        Se llama desde los botones "+ Subir CSV".
        Prepara el evento (si es necesario) y luego lee el archivo.
        """
        pagina_actual = self.currentIndex()

        # 1. Comprobar si tenemos un evento listo
        if pagina_actual == 1: # Si estamos en "Crear Evento"
            # Si el evento temporal no existe, lo creamos
            if self.evento_en_edicion_actual is None:
                if not self._crear_evento_temporal_desde_pagina1():
                    return # Falla si el ayudante no puede crear el evento
        
        elif pagina_actual == 2: # Si estamos en "Actualizar Evento"
            if self.evento_en_edicion_actual is None:
                QMessageBox.critical(self, "Error", "No hay evento seleccionado (esto no debería pasar)")
                return
        
        # 2. Abrir el diálogo para seleccionar archivo
        # Abre el explorador de archivos, filtrando por archivos CSV
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(self, "Seleccionar CSV de Participantes", "", "Archivos CSV (*.csv);;Todos los archivos (*)", options=options)

        # Si el usuario cancela, filePath estará vacío
        if not filePath:
            return # No hacer nada

        # 3. Leer el archivo CSV
        try:
            participantes_cargados = 0
            with open(filePath, mode='r', encoding='utf-8') as f:
                # 'csv.DictReader' lee la primera fila como cabeceras
                reader = csv.DictReader(f)
                
                for row in reader:
                    # --- MODIFICADO: Búsqueda de encabezado más flexible (mayús/minús) ---
                    nombre_participante = row.get('Nombre') or row.get('nombre')
                    
                    if not nombre_participante: # Ignorar filas sin nombre
                        continue
                        
                    # Crear el participante (misma lógica que anadir_participante_al_evento)
                    evento_id = self.evento_en_edicion_actual.IdEvento
                    num_part = len(self.evento_en_edicion_actual.participantes)
                    participante_id = f"{evento_id}_p_{num_part + 1}"
                    
                    nuevo_participante = Participante(participante_id, nombre_participante)

                    # Añadir preferencias
                    pref_texto = row.get('Preferencias') or row.get('preferencias', '') # Coge el texto o un string vacío
                    if pref_texto:
                        # Separa los nombres por ";" y quita espacios en blanco
                        lista_pref = [nombre.strip() for nombre in pref_texto.split(';') if nombre.strip()]
                        nuevo_participante.preferencias = lista_pref

                    # Añadir evitados
                    evit_texto = row.get('Evitados') or row.get('evitados', '')
                    if evit_texto:
                        lista_evit = [nombre.strip() for nombre in evit_texto.split(';') if nombre.strip()]
                        nuevo_participante.evitados = lista_evit
                    # --- FIN MODIFICADO ---
                    
                    # Añadir el participante al evento
                    self.evento_en_edicion_actual.anadirparticipante(nuevo_participante)
                    participantes_cargados += 1

            QMessageBox.information(self, "Éxito", f"Se han cargado {participantes_cargados} participantes desde el CSV.")
            
            # --- NUEVO: Si estamos en Pág 2 (Actualizar), guardamos los cambios del CSV inmediatamente ---
            if pagina_actual == 2:
                self.gestor_datos.guardarEventos(self.lista_eventos)
            # --- FIN NUEVO ---

        except Exception as e:
            QMessageBox.critical(self, "Error al leer CSV", f"No se pudo leer el archivo.\nError: {e}")

    # --- INICIO CÓDIGO NUEVO (TODAS LAS FUNCIONES PARA PÁGINAS 4, 6 y 8) ---
    
    # --- Lógica para Asignación Manual (Página 4) ---

    def actualizar_listas_manual(self):
        """ Actualiza las listas de la página de asignación manual. """
        if not self.evento_en_edicion_actual or not self.evento_en_edicion_actual.mesas:
            return

        # 1. Obtener la mesa actual
        mesa_actual = self.evento_en_edicion_actual.mesas[self.mesa_manual_actual_idx]
        self.pagina_manual.ui.Label_TableParticipants.setText(f"Mesa {mesa_actual.numero} ({len(mesa_actual.participantes)}/{mesa_actual.capacidad})")

        # 2. Llenar lista de participantes de la mesa
        lista_mesa_ui = self.pagina_manual.ui.List_TableParticipants
        lista_mesa_ui.clear()
        for p in mesa_actual.participantes:
            lista_mesa_ui.addItem(p.nombre)

        # 3. Llenar lista de participantes sin asignar
        lista_sin_asignar_ui = self.pagina_manual.ui.List_UnassignedGuests
        lista_sin_asignar_ui.clear()
        
        participantes_asignados_ids = set()
        for m in self.evento_en_edicion_actual.mesas:
            for p in m.participantes:
                participantes_asignados_ids.add(p.id_participante)

        for p in self.evento_en_edicion_actual.participantes:
            if p.id_participante not in participantes_asignados_ids:
                lista_sin_asignar_ui.addItem(p.nombre)

    def manual_siguiente_mesa(self):
        if not self.evento_en_edicion_actual: return
        num_mesas = len(self.evento_en_edicion_actual.mesas)
        if num_mesas > 0:
            self.mesa_manual_actual_idx = (self.mesa_manual_actual_idx + 1) % num_mesas
            self.actualizar_listas_manual()

    def manual_anterior_mesa(self):
        if not self.evento_en_edicion_actual: return
        num_mesas = len(self.evento_en_edicion_actual.mesas)
        if num_mesas > 0:
            self.mesa_manual_actual_idx = (self.mesa_manual_actual_idx - 1) % num_mesas
            self.actualizar_listas_manual()

    def manual_anadir_participante(self):
        """ Mueve un participante de 'Sin Asignar' a la mesa actual. """
        item_seleccionado = self.pagina_manual.ui.List_UnassignedGuests.currentItem()
        if not item_seleccionado or not self.evento_en_edicion_actual:
            return

        mesa_actual = self.evento_en_edicion_actual.mesas[self.mesa_manual_actual_idx]
        if mesa_actual.estaLlena():
            QMessageBox.warning(self, "Mesa Llena", f"La Mesa {mesa_actual.numero} ya está llena.")
            return

        # Buscar el objeto Participante por su nombre
        nombre_p = item_seleccionado.text()
        participante_a_mover = None
        
        # Buscamos al participante que tenga ese nombre Y NO esté asignado
        participantes_asignados_ids = set()
        for m in self.evento_en_edicion_actual.mesas:
            for p in m.participantes:
                participantes_asignados_ids.add(p.id_participante)
        
        for p in self.evento_en_edicion_actual.participantes:
            if p.nombre == nombre_p and p.id_participante not in participantes_asignados_ids:
                participante_a_mover = p
                break
        
        if participante_a_mover:
            mesa_actual.anadirParticipante(participante_a_mover)
            participante_a_mover.asignar_mesa(mesa_actual.id_mesa)
            self.actualizar_listas_manual()
            self.gestor_datos.guardarEventos(self.lista_eventos) # Guardar cambios

    def manual_eliminar_participante(self):
        """ Mueve un participante de la mesa actual a 'Sin Asignar'. """
        item_seleccionado = self.pagina_manual.ui.List_TableParticipants.currentItem()
        if not item_seleccionado or not self.evento_en_edicion_actual:
            return

        mesa_actual = self.evento_en_edicion_actual.mesas[self.mesa_manual_actual_idx]
        
        # Buscar el objeto Participante por su nombre
        nombre_p = item_seleccionado.text()
        participante_a_mover = None
        for p in mesa_actual.participantes:
            if p.nombre == nombre_p:
                participante_a_mover = p
                break

        if participante_a_mover:
            mesa_actual.eliminarParticipante(participante_a_mover)
            participante_a_mover.quitar_mesa()
            self.actualizar_listas_manual()
            self.gestor_datos.guardarEventos(self.lista_eventos) # Guardar cambios

    # --- Lógica para Gestión de Participantes (Página 6) ---

    # --- NUEVO: Esta función se activa cuando el usuario escribe en el QLineEdit ---
    def limpiar_participante_en_gestion(self, texto):
        """
        Si el usuario escribe en el campo de texto,
        asumimos que quiere crear uno nuevo, así que limpiamos la selección.
        """
        # Solo limpiamos si el texto es diferente al del participante gestionado
        if self.participante_en_gestion and texto != self.participante_en_gestion.nombre:
            self.participante_en_gestion = None
            self.pagina_participantes.ui.List_AllGuests.clearSelection()
            self.actualizar_listas_preferencias()
    # --- FIN NUEVO ---

    # --- MODIFICADO: Esta función se activa al hacer DOBLE CLIC en un invitado ---
    def gestionar_participante_seleccionado(self, item):
        """ 
        Se activa al hacer DOBLE CLIC en un nombre en la lista 'Todos los Invitados'.
        Carga a este participante para editarlo.
        """
        if item is None: # Si se des-selecciona
            self.participante_en_gestion = None
            self.pagina_participantes.ui.Input_ParticipantName.setText("")
            self.actualizar_listas_preferencias()
            return
            
        nombre_p = item.text()
        self.participante_en_gestion = None
        
        if self.evento_en_edicion_actual:
            for p in self.evento_en_edicion_actual.participantes:
                if p.nombre == nombre_p:
                    self.participante_en_gestion = p
                    break
        
        if self.participante_en_gestion:
            # Cargar el nombre en el campo de texto
            self.pagina_participantes.ui.Input_ParticipantName.setText(self.participante_en_gestion.nombre)
            # Cargar sus preferencias
            self.actualizar_listas_preferencias()
    # --- FIN MODIFICADO ---

    def actualizar_listas_preferencias(self):
        """ Actualiza las listas de Preferencia y Evitados para el participante seleccionado. """
        lista_pref = self.pagina_participantes.ui.List_Preference
        lista_evit = self.pagina_participantes.ui.List_Avoid
        
        lista_pref.clear()
        lista_evit.clear()

        if self.participante_en_gestion:
            # Rellenamos las listas con los nombres guardados en el objeto participante
            for nombre_pref in self.participante_en_gestion.preferencias:
                lista_pref.addItem(nombre_pref)
            for nombre_evit in self.participante_en_gestion.evitados:
                lista_evit.addItem(nombre_evit)

    # --- MODIFICADO: Esta función ahora usa el flujo correcto ---
    def participante_anadir_preferencia(self):
        """ 
        Añade el participante seleccionado en "Todos" a la lista de "Preferencia"
        del participante que se está gestionando (el del campo de texto).
        """
        if not self.participante_en_gestion:
            QMessageBox.warning(self, "Error", "Primero añade o selecciona (con doble clic) un participante (ej: 'Asa') para editarlo.")
            return

        item_seleccionado = self.pagina_participantes.ui.List_AllGuests.currentItem()
        if not item_seleccionado:
            QMessageBox.warning(self, "Error", "Ahora, selecciona (con un solo clic) a *otro* participante de la lista 'Todos los Invitados' (ej: 'Pepica') para añadir a sus preferencias.")
            return
            
        nombre_a_anadir = item_seleccionado.text()

        if nombre_a_anadir == self.participante_en_gestion.nombre:
            QMessageBox.warning(self, "Error", "No puedes añadir a un participante a sus propias preferencias.")
            return
            
        # Añadir al objeto y actualizar UI
        if self.participante_en_gestion.anadir_preferencia(nombre_a_anadir):
            # Quitar de la lista de evitados si estaba
            self.participante_en_gestion.eliminar_evitado(nombre_a_anadir)
            self.actualizar_listas_preferencias() # Refresca la UI
            
            # --- MODIFICADO: Corregir el 'TypeError' ---
            # Guardar cambios en el JSON si estamos en el flujo de "Actualizar"
            if self.modo_gestion_participantes == "ACTUALIZAR":
                self.gestor_datos.guardarEventos(self.lista_eventos)
            # --- FIN MODIFICADO ---
    # --- FIN MODIFICADO ---

    # --- MODIFICADO: Esta función ahora usa el flujo correcto ---
    def participante_anadir_evitado(self):
        """ 
        Añade el participante seleccionado en "Todos" a la lista de "No Acepta"
        del participante que se está gestionando (el del campo de texto).
        """
        if not self.participante_en_gestion:
            QMessageBox.warning(self, "Error", "Primero añade o selecciona (con doble clic) un participante (ej: 'Asa') para editarlo.")
            return

        item_seleccionado = self.pagina_participantes.ui.List_AllGuests.currentItem()
        if not item_seleccionado:
            QMessageBox.warning(self, "Error", "Ahora, selecciona (con un solo clic) a *otro* participante de la lista 'Todos los Invitados' (ej: 'Pepica') para añadir a sus evitados.")
            return

        nombre_a_anadir = item_seleccionado.text()

        if nombre_a_anadir == self.participante_en_gestion.nombre:
            QMessageBox.warning(self, "Error", "No puedes añadir a un participante a su propia lista de evitados.")
            return

        if self.participante_en_gestion.anadir_evitado(nombre_a_anadir):
            # Quitar de la lista de preferencias si estaba
            self.participante_en_gestion.eliminar_preferencia(nombre_a_anadir)
            self.actualizar_listas_preferencias() # Refresca la UI
            
            # --- MODIFICADO: Corregir el 'TypeError' ---
            # Guardar cambios en el JSON si estamos en el flujo de "Actualizar"
            if self.modo_gestion_participantes == "ACTUALIZAR":
                self.gestor_datos.guardarEventos(self.lista_eventos)
            # --- FIN MODIFICADO ---
    # --- FIN MODIFICADO ---

    def participante_eliminar_relacion(self):
        """ Elimina un nombre de la lista 'Preferencia' O 'No Acepta'. """
        if not self.participante_en_gestion:
            QMessageBox.warning(self, "Error", "No hay ningún participante seleccionado para editar.")
            return

        # Comprobar si hay algo seleccionado en Preferencias
        item_pref = self.pagina_participantes.ui.List_Preference.currentItem()
        if item_pref:
            self.participante_en_gestion.eliminar_preferencia(item_pref.text())
            self.actualizar_listas_preferencias()
            return

        # Comprobar si hay algo seleccionado en No Acepta
        item_evit = self.pagina_participantes.ui.List_Avoid.currentItem()
        if item_evit:
            self.participante_en_gestion.eliminar_evitado(item_evit.text())
            self.actualizar_listas_preferencias()
            return

    # --- Lógica para Gestión de Excepciones (Página 8) ---
    
    def actualizar_listas_excepciones_ui(self):
        """ Actualiza las listas de la página de excepciones. """
        if not self.evento_en_edicion_actual or not self.evento_en_edicion_actual.mesas:
            return

        # 1. Obtener la mesa actual
        mesa_actual = self.evento_en_edicion_actual.mesas[self.excepcion_mesa_actual_idx]
        self.pagina_excepciones.ui.Label_TableParticipants.setText(f"Mesa {mesa_actual.numero} ({len(mesa_actual.participantes)}/{mesa_actual.capacidad})")

        # 2. Llenar lista de participantes de la mesa
        lista_mesa_ui = self.pagina_excepciones.ui.List_TableParticipants
        lista_mesa_ui.clear()
        for p in mesa_actual.participantes:
            lista_mesa_ui.addItem(p.nombre)

        # 3. Llenar lista de participantes con conflicto (excepciones)
        lista_excepciones_ui = self.pagina_excepciones.ui.List_Exceptions
        lista_excepciones_ui.clear()
        for p in self.lista_excepciones:
            lista_excepciones_ui.addItem(p.nombre)

    def excepcion_siguiente_mesa(self):
        if not self.evento_en_edicion_actual: return
        num_mesas = len(self.evento_en_edicion_actual.mesas)
        if num_mesas > 0:
            self.excepcion_mesa_actual_idx = (self.excepcion_mesa_actual_idx + 1) % num_mesas
            self.actualizar_listas_excepciones_ui()

    def excepcion_anterior_mesa(self):
        if not self.evento_en_edicion_actual: return
        num_mesas = len(self.evento_en_edicion_actual.mesas)
        if num_mesas > 0:
            self.excepcion_mesa_actual_idx = (self.excepcion_mesa_actual_idx - 1) % num_mesas
            self.actualizar_listas_excepciones_ui()

    def excepcion_anadir_participante(self):
        """ Mueve un participante de 'Excepciones' a la mesa actual. """
        item_seleccionado = self.pagina_excepciones.ui.List_Exceptions.currentItem()
        if not item_seleccionado or not self.evento_en_edicion_actual:
            return

        mesa_actual = self.evento_en_edicion_actual.mesas[self.excepcion_mesa_actual_idx]
        if mesa_actual.estaLlena():
            QMessageBox.warning(self, "Mesa Llena", f"La Mesa {mesa_actual.numero} ya está llena.")
            return

        # Buscar el objeto Participante por su nombre
        nombre_p = item_seleccionado.text()
        participante_a_mover = None
        for p in self.lista_excepciones:
            if p.nombre == nombre_p:
                participante_a_mover = p
                break
        
        if participante_a_mover:
            mesa_actual.anadirParticipante(participante_a_mover)
            participante_a_mover.asignar_mesa(mesa_actual.id_mesa)
            self.lista_excepciones.remove(participante_a_mover) # Quitar de excepciones
            self.actualizar_listas_excepciones_ui()
            self.gestor_datos.guardarEventos(self.lista_eventos) # Guardar cambios

    def excepcion_eliminar_participante(self):
        """ Mueve un participante de la mesa actual de vuelta a 'Excepciones'. """
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
            mesa_actual.eliminarParticipante(participante_a_mover)
            participante_a_mover.quitar_mesa()
            self.lista_excepciones.append(participante_a_mover) # Devolver a excepciones
            self.actualizar_listas_excepciones_ui()
            self.gestor_datos.guardarEventos(self.lista_eventos) # Guardar cambios

    # --- Lógica para Generar CSV (Página 0) ---

    def generar_csv_evento_seleccionado(self):
        tabla_crud = self.pagina_crud.ui.EventList_Table
        fila_seleccionada = tabla_crud.currentRow()

        if fila_seleccionada == -1:
            QMessageBox.warning(self, "Error", "Selecciona un evento para generar el CSV.")
            return

        try:
            evento_seleccionado = self.lista_eventos[fila_seleccionada]
        except IndexError:
            QMessageBox.critical(self, "Error", "Error al obtener el evento.")
            return

        # Abrir diálogo para guardar archivo
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getSaveFileName(self, "Guardar CSV de Participantes", f"{evento_seleccionado.nombre}_participantes.csv", "Archivos CSV (*.csv);;Todos los archivos (*)", options=options)

        if not filePath:
            return # Usuario canceló

        try:
            with open(filePath, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                
                # Escribir cabeceras
                writer.writerow(["Nombre", "Preferencias", "Evitados"])
                
                # Escribe datos de participantes
                for p in evento_seleccionado.participantes:
                    # Une listas con ";"
                    preferencias_str = ";".join(p.preferencias)
                    evitados_str = ";".join(p.evitados)
                    writer.writerow([p.nombre, preferencias_str, evitados_str])
            
            QMessageBox.information(self, "Éxito", f"CSV generado exitosamente en:\n{filePath}")

        except Exception as e:
            QMessageBox.critical(self, "Error al escribir CSV", f"No se pudo guardar el archivo.\nError: {e}")



#Ejecuta
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec_())