# Chupa todas las librerias
# Las cosas que necesita el programa
import sys
import os
import webbrowser
import csv
from PyQt5.QtWidgets import QApplication, QWidget, QStackedWidget, QMessageBox, QTableWidgetItem, QFileDialog
from ortools.sat.python import cp_model
import random

# Trae todas las pantallas
# Las que están en 'controllers'
from controllers.CrudEvento import Ui_MainWindow
from controllers.ControllerCrearEvento1 import Ui_Form as Ui_CrearEventoForm
from controllers.ControllerAsignarMesas import Ui_Form as Ui_PaginaMesas
from controllers.EditarEvento import Ui_Form as Ui_ActualizarEventoForm
from controllers.ControllerAsignarMesasManual import Ui_Form as Ui_AsignarManual
from controllers.ControllerBorrarEvento import Ui_DialogoBorrarEvento as Ui_Borrar
from controllers.ControllerAsignarMesasAutomatico import Ui_Form as Ui_ResultadosAuto
from controllers.ControllerAsignarMesasExcepciones import Ui_Form as Ui_Excepciones

from controllers.ControllerCrearEvento2 import Ui_DialogoParticipantes

# Trae los moldes
# Los de 'clases'
# Evento Participante Mesa
from clases.GestorDatos import GestorDatos
from clases.Evento import Evento
from clases.Participante import Participante
from clases.Mesa import Mesa


# Molde para la pantalla principal
# La del CRUD
class PaginaCrud(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

# Molde para la pantalla de crear evento
class PaginaCrearEvento(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_CrearEventoForm()
        self.ui.setupUi(self)

# Molde para la pantalla de asignar mesas
class PaginaMesas(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_PaginaMesas()
        self.ui.setupUi(self)
        
# Molde para la pantalla de actualizar evento
class PaginaActualizarEvento(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ActualizarEventoForm()
        self.ui.setupUi(self)

# Molde para la pantalla de asignar mesas a mano
class Manual(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_AsignarManual()
        self.ui.setupUi(self)  

# Molde para la pantalla de borrar
class PaginaBorrar(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Borrar()
        self.ui.setupUi(self)

# Molde para la pantalla de gestionar invitados
class PaginaGestionarParticipantes(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_DialogoParticipantes()
        self.ui.setupUi(self)

# Molde para la pantalla de resultados automáticos
class PaginaMesasAutomatico(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ResultadosAuto()
        self.ui.setupUi(self)

# Molde para la pantalla de excepciones
class PaginaExcepciones(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Excepciones()
        self.ui.setupUi(self)

# La ventana jefa
# La que manda todo
class VentanaPrincipal(QStackedWidget):
    def __init__(self):
        super().__init__()
        
        # El que guarda en el JSON
        self.gestor_datos = GestorDatos("eventos.json") 
        # Una lista para todos los eventos
        self.lista_eventos = []
        # El evento que estamos tocando ahora
        self.evento_en_edicion_actual = None
        # Los que no caben en automático
        self.lista_excepciones = []

        # Variables para saber qué estamos haciendo
        self.modo_gestion_participantes = None # Puede ser "CREAR" o "ACTUALIZAR"
        self.participante_en_gestion = None # El invitado que estamos editando
        self.mesa_manual_actual_idx = 0     # El número de mesa que vemos en manual
        self.excepcion_mesa_actual_idx = 0  # El número de mesa en excepciones
        self.CSV_EXPORT_PATH = "CSVs_Generados" # Donde van los CSVs que creamos

        # Crea todas las pantallas
        self.pagina_crud = PaginaCrud()           #0
        self.pagina_crear = PaginaCrearEvento()     #1
        self.pagina_actualizar = PaginaActualizarEvento() #2
        self.pagina_mesas = PaginaMesas()         #3
        self.pagina_manual=Manual()             #4
        self.pagina_borrar=PaginaBorrar()       #5
        self.pagina_participantes = PaginaGestionarParticipantes() #6
        self.pagina_resultados_auto = PaginaMesasAutomatico() #7
        self.pagina_excepciones = PaginaExcepciones() #8
        
        # Mete todas las pantallas en el taco
        self.addWidget(self.pagina_crud)           #0
        self.addWidget(self.pagina_crear)         #1
        self.addWidget(self.pagina_actualizar)    #2
        self.addWidget(self.pagina_mesas)          #3
        self.addWidget(self.pagina_manual)          #4
        self.addWidget(self.pagina_borrar)         #5
        self.addWidget(self.pagina_participantes)  #6
        self.addWidget(self.pagina_resultados_auto) #7
        self.addWidget(self.pagina_excepciones) #8

        # Aquí conectamos los botones
        # Click y acción
        # Botones de la pantalla principal (CRUD)
        self.pagina_crud.ui.CreateEvent_Btn.clicked.connect(self.mostrar_pagina_crear)
        self.pagina_crud.ui.UpdateEvent_Btn.clicked.connect(self.mostrar_pagina_actualizar)
        self.pagina_crud.ui.AssignTables_Btn.clicked.connect(self.mostrar_pagina_mesas)
        self.pagina_crud.ui.DeleteEvent_Btn.clicked.connect(self.mostrar_pagina_borrar)
        
        # Botón auto llama al super algoritmo
        self.pagina_mesas.ui.AutoAssign_Btn.clicked.connect(self.ejecutar_asignacion_automatica)
        
        # Botón ver excepciones
        self.pagina_resultados_auto.ui.ViewExceptions_Btn.clicked.connect(self.mostrar_pagina_excepciones)

        # Botones de otras pantallas
        self.pagina_mesas.ui.ManualAssign_Btn.clicked.connect(self.mostrar_pagina_manual)
        self.pagina_crear.ui.CreateManual_Btn.clicked.connect(self.preparar_evento_para_participantes)
        
        # Botón abrir CSV te abre la carpeta
        self.pagina_crud.ui.OpenCSVPath_Btn.clicked.connect(self.abrir_carpeta_csvs)
        
        # Botones de subir CSV
        self.pagina_crear.ui.UploadCSV_Btn.clicked.connect(self.cargar_participantes_csv)
        self.pagina_actualizar.ui.UploadCSV_Btn.clicked.connect(self.cargar_participantes_csv)

        # Botón manual en actualizar
        # Llama a la función de actualizar
        self.pagina_actualizar.ui.CreateManual_Btn.clicked.connect(self.mostrar_pagina_participantes_actualizar)

        # Botones de atrás
        self.pagina_crear.ui.BackButton_CreateEvent.clicked.connect(self.mostrar_pagina_crud)
        self.pagina_crear.ui.FinishCreateEvent_Btn.clicked.connect(self.guardar_nuevo_evento)
        self.pagina_actualizar.ui.BackButton_UpdateEvent.clicked.connect(self.mostrar_pagina_crud)
        self.pagina_mesas.ui.BackButton_AssignMenu.clicked.connect(self.mostrar_pagina_crud)
        self.pagina_borrar.ui.BackButton_DeleteEvent.clicked.connect(self.mostrar_pagina_crud)

        # Botón confirmar borrado
        self.pagina_borrar.ui.ConfirmDelete_Btn.clicked.connect(self.borrar_evento_seleccionado)

        # Botón guardar cambios (actualizar)
        self.pagina_actualizar.ui.SaveUpdate_Btn.clicked.connect(self.guardar_evento_actualizado)
        
        # Conexiones de la PÁGINA 6 (Gestionar Participantes)
        # El botón de atrás y finalizar se conectan luego
        self.pagina_participantes.ui.Add_Btn.clicked.connect(self.anadir_participante_al_evento)
        
        # Doble clic en un invitado lo carga
        self.pagina_participantes.ui.List_AllGuests.itemDoubleClicked.connect(self.gestionar_participante_seleccionado)
        
        # Si escribes en el nombre limpia la selección
        self.pagina_participantes.ui.Input_ParticipantName.textChanged.connect(self.limpiar_participante_en_gestion)

        # Botones V X y Eliminar
        self.pagina_participantes.ui.MoveToPreference_Btn.clicked.connect(self.participante_anadir_preferencia)
        self.pagina_participantes.ui.MoveToAvoid_Btn.clicked.connect(self.participante_anadir_evitado)
        self.pagina_participantes.ui.RemoveFromList_Btn.clicked.connect(self.participante_eliminar_relacion)

        # Botón atrás de asignar manual
        self.pagina_manual.ui.BackButton_ManualAssign.clicked.connect(self.mostrar_pagina_mesas)

        # Conexiones de la PÁGINA 4 (Asignación Manual)
        self.pagina_manual.ui.NextTable_Btn.clicked.connect(self.manual_siguiente_mesa)
        self.pagina_manual.ui.PrevTable_Btn.clicked.connect(self.manual_anterior_mesa)
        self.pagina_manual.ui.AddParticipant_Btn.clicked.connect(self.manual_anadir_participante)
        self.pagina_manual.ui.RemoveParticipant_Btn.clicked.connect(self.manual_eliminar_participante)

        # Botón atrás de automático 
        self.pagina_resultados_auto.ui.BackButton_AutoAssign.clicked.connect(self.mostrar_pagina_mesas)

        # Botón atrás excepciones
        self.pagina_excepciones.ui.BackButton_Exceptions.clicked.connect(self.mostrar_pagina_auto)
        
        # Conexiones de la PÁGINA 8 (Excepciones)
        self.pagina_excepciones.ui.NextTable_Btn.clicked.connect(self.excepcion_siguiente_mesa)
        self.pagina_excepciones.ui.PrevTable_Btn.clicked.connect(self.excepcion_anterior_mesa)
        self.pagina_excepciones.ui.AddParticipant_Btn.clicked.connect(self.excepcion_anadir_participante)
        self.pagina_excepciones.ui.RemoveParticipant_Btn.clicked.connect(self.excepcion_eliminar_participante)
        
        # Botón generar CSV llama a su función
        self.pagina_crud.ui.GenerateCSV_Btn.clicked.connect(self.generar_csv_evento_seleccionado)
        
        # Pone el tamaño de la ventana
        self.resize(904, 617)
        # Carga los datos del JSON al empezar
        self.cargar_y_actualizar_eventos()


    # Métodos para cambiar de pantalla
    def mostrar_pagina_crud(self):
        self.actualizar_tabla_crud()
        self.setCurrentIndex(0)
        
    def mostrar_pagina_crear(self):
        # Limpia todo por si acaso
        self.evento_en_edicion_actual = None
        self.participante_en_gestion = None
        self.pagina_participantes.ui.Input_ParticipantName.setText("")
        self.actualizar_listas_participantes()
        self.setCurrentIndex(1) 

    def mostrar_pagina_actualizar(self):
        # Pilla la tabla principal
        tabla_crud = self.pagina_crud.ui.EventList_Table
        
        # Pilla la fila que has pinchado
        fila_seleccionada = tabla_crud.currentRow()

        # Si no has pillado nada te avisa
        if fila_seleccionada == -1:
            QMessageBox.warning(self, "Error", "Selecciona un evento para editar")
            return # Y se pira

        # Intenta pillar el evento de la lista
        try:
            # Lo guarda como evento actual
            self.evento_en_edicion_actual = self.lista_eventos[fila_seleccionada]
            # Limpia al invitado por si acaso
            self.participante_en_gestion = None
            self.pagina_participantes.ui.Input_ParticipantName.setText("")
            self.actualizar_listas_participantes()
        except IndexError:
            QMessageBox.critical(self, "Error")
            return

        # Rellena los campos con los datos del evento
        self.pagina_actualizar.ui.Input_EventName.setText(self.evento_en_edicion_actual.nombre)
        self.pagina_actualizar.ui.Input_EventDate.setText(self.evento_en_edicion_actual.fecha)
        self.pagina_actualizar.ui.Input_EventLocation.setText(self.evento_en_edicion_actual.ubicacion)
        self.pagina_actualizar.ui.Input_EventOrganizer.setText(self.evento_en_edicion_actual.organizador)
        self.pagina_actualizar.ui.Input_NumTables.setValue(self.evento_en_edicion_actual.numMesas)
        
        # Pone la pagina
        self.setCurrentIndex(2)

    def mostrar_pagina_mesas(self):

        # Pilla la tabla principal
        tabla_crud = self.pagina_crud.ui.EventList_Table
        # Pilla la fila seleccionada
        fila_seleccionada = tabla_crud.currentRow()

        # Si no pillas evento te avisa
        if fila_seleccionada == -1:
            QMessageBox.warning(self, "Sin selección", "Por favor, selecciona un evento para asignar sus mesas.")
            return

        # Pilla el evento de la lista
        try:
            self.evento_en_edicion_actual = self.lista_eventos[fila_seleccionada]
            print(f"Gestionando mesas para el evento: {self.evento_en_edicion_actual.nombre}")
        except IndexError:
            QMessageBox.critical(self, "Error")
            return # Se pira

        # Abre la página asignar mesas
        self.setCurrentIndex(3)

    # Enseña la pantalla de mesas manual
    def mostrar_pagina_manual(self):
        # Si no hay evento te echa
        if self.evento_en_edicion_actual is None:
            QMessageBox.warning(self, "Error", "No hay evento seleccionado.")
            return
            
        self.mesa_manual_actual_idx = 0 # Empieza por la mesa 0
        self.actualizar_listas_manual() # Recarga las listas de la pantalla
        self.setCurrentIndex(4) # Enseña la pantalla 4

    def mostrar_pagina_borrar(self):
        self.setCurrentIndex(5)
        # Recarga la tabla de borrar
        self.cargar_y_actualizar_eventos_borrar()
    


    # Más métodos
    # Este prepara la pantalla de invitados para CREAR evento
    def preparar_evento_para_participantes(self):
        
        # Si no hay evento temporal lo crea
        if self.evento_en_edicion_actual is None:
            if not self._crear_evento_temporal_desde_pagina1():
                return # Si falla al crearlo se pira
        
        # Actualiza las listas de invitados
        self.actualizar_listas_participantes()
        
        # Pone el modo en CREAR
        self.modo_gestion_participantes = "CREAR" 
        try:
            # Limpia los botones por si acaso
            self.pagina_participantes.ui.BackButton_Participants.clicked.disconnect()
            self.pagina_participantes.ui.Finish_Btn.clicked.disconnect()
        except TypeError:
            pass # No pasa nada si no estaban conectadas
            
        # Botón atrás vuelve a crear
        self.pagina_participantes.ui.BackButton_Participants.clicked.connect(self.mostrar_pagina_crear)
        # Botón finalizar guarda el evento nuevo
        self.pagina_participantes.ui.Finish_Btn.clicked.connect(self.guardar_evento_y_participantes)
        
        self.setCurrentIndex(6) # Enseña la pantalla 6

    # Este prepara la pantalla de invitados para ACTUALIZAR evento
    def mostrar_pagina_participantes_actualizar(self):
        
        # Si no hay evento te echa
        if self.evento_en_edicion_actual is None:
            QMessageBox.critical(self, "Error", "No hay ningún evento seleccionado. Esto no debería pasar.")
            return

        # Actualiza las listas
        self.actualizar_listas_participantes()
        
        # Pone el modo en ACTUALIZAR
        self.modo_gestion_participantes = "ACTUALIZAR" 
        try:
            # Limpia los botones
            self.pagina_participantes.ui.BackButton_Participants.clicked.disconnect()
            self.pagina_participantes.ui.Finish_Btn.clicked.disconnect()
        except TypeError:
            pass # No pasa nada
            
        # Botón atrás vuelve a actualizar
        self.pagina_participantes.ui.BackButton_Participants.clicked.connect(self.mostrar_pagina_actualizar)
        # Botón finalizar solo vuelve
        # No guarda
        self.pagina_participantes.ui.Finish_Btn.clicked.connect(self.mostrar_pagina_actualizar)
        
        self.setCurrentIndex(6) # Enseña la pantalla 6

    # Añade un invitado nuevo
    # El que escribes en el campo
    def anadir_participante_al_evento(self):
        
        # 1. Si no hay evento lo crea temporal
        if self.evento_en_edicion_actual is None:
             if not self._crear_evento_temporal_desde_pagina1():
                return # Si falla se pira
        
        # 2. Pilla el nombre del campo
        nombre_participante = self.pagina_participantes.ui.Input_ParticipantName.text().strip()
        # Si está vacío te avisa
        if not nombre_participante:
            QMessageBox.warning(self, "Oye", "Escribe el nombre del participante.")
            return
            
        # 3. Mira si el nombre ya existe
        for p in self.evento_en_edicion_actual.participantes:
            if p.nombre.lower() == nombre_participante.lower():
                QMessageBox.warning(self, "Duplicado", f"El participante '{nombre_participante}' ya existe en este evento.")
                return

        # 4. Crea un ID único para el invitado
        evento_id = self.evento_en_edicion_actual.IdEvento
        num_part = len(self.evento_en_edicion_actual.participantes)
        participante_id = f"{evento_id}_p_{num_part + 1}"

        # Crea el objeto Participante
        nuevo_participante = Participante(participante_id, nombre_participante)
        # Lo mete en la lista del evento
        self.evento_en_edicion_actual.anadirparticipante(nuevo_participante)
        
        # 5. Lo pone como invitado actual
        # Para editarlo ahora
        self.participante_en_gestion = nuevo_participante
        
        # 6. Recarga la lista de 'Todos'
        self.actualizar_listas_participantes()
        
        # 7. Busca al nuevo en la lista
        # Y lo pone en azul
        for i in range(self.pagina_participantes.ui.List_AllGuests.count()):
            item = self.pagina_participantes.ui.List_AllGuests.item(i)
            if item.text() == nombre_participante:
                item.setSelected(True)
                # Carga sus listas (vacías)
                self.actualizar_listas_preferencias()
                break
        
        # 8. Si estamos en modo actualizar
        # Guarda en el JSON al momento
        if self.modo_gestion_participantes == "ACTUALIZAR":
            self.gestor_datos.guardarEventos(self.lista_eventos)

    def actualizar_listas_participantes(self):
        # Recarga la lista 'Todos los Invitados'
        # Limpia las listas de prefs y evitados
        lista_invitados = self.pagina_participantes.ui.List_AllGuests
        lista_pref = self.pagina_participantes.ui.List_Preference
        lista_no = self.pagina_participantes.ui.List_Avoid
        
        # Vacía las tres listas
        lista_invitados.clear()
        lista_pref.clear()
        lista_no.clear()

        # Si hay un evento...
        if self.evento_en_edicion_actual:
            # Recorre los invitados y los mete en la lista
            for participante in self.evento_en_edicion_actual.participantes:
                lista_invitados.addItem(participante.nombre)
        
        # Quita la selección azul
        self.pagina_participantes.ui.List_AllGuests.clearSelection()
        
    def guardar_evento_y_participantes(self):
        # Guarda el evento NUEVO
        # Se llama desde el botón Finalizar de crear
        if self.evento_en_edicion_actual is None:
            QMessageBox.critical(self, "Error", "No hay evento que guardar.")
            return
            
        # Mira si ya está en la lista principal
        evento_existe = False
        for ev in self.lista_eventos:
            if ev.IdEvento == self.evento_en_edicion_actual.IdEvento:
                evento_existe = True
                break
        
        # Si no está lo añade
        if not evento_existe:
             self.lista_eventos.append(self.evento_en_edicion_actual)
        
        # Guarda todo en el JSON
        self.gestor_datos.guardarEventos(self.lista_eventos)

        # Limpia las variables
        self.evento_en_edicion_actual = None
        self.participante_en_gestion = None 
        
        # Limpia los campos de la pantalla crear
        self.pagina_crear.ui.Input_EventName.setText("")
        self.pagina_crear.ui.Input_EventDate.setText("")
        self.pagina_crear.ui.Input_EventLocation.setText("")
        self.pagina_crear.ui.Input_EventOrganizer.setText("")
        self.pagina_crear.ui.Input_NumTables.setValue(1)
        
        # Limpia la pantalla de invitados
        self.pagina_participantes.ui.Input_ParticipantName.setText("")
        self.actualizar_listas_participantes()

        # Vuelve al menú principal
        self.mostrar_pagina_crud()


# Guarda los cambios de un evento existente
    def guardar_evento_actualizado(self):

        # Pilla todos los datos de los campos
        nuevo_nombre = self.pagina_actualizar.ui.Input_EventName.text()
        nueva_fecha = self.pagina_actualizar.ui.Input_EventDate.text()
        nueva_ubicacion = self.pagina_actualizar.ui.Input_EventLocation.text()
        nuevo_organizador = self.pagina_actualizar.ui.Input_EventOrganizer.text()
        nuevo_numMesas = self.pagina_actualizar.ui.Input_NumTables.value()

        # Si falta nombre o fecha te avisa
        if not nuevo_nombre or not nueva_fecha:
            QMessageBox.warning(self,  "Oye", "Pon el nombre y la fecha")       
            return #sale del metodo

        # Actualiza el objeto evento
        self.evento_en_edicion_actual.nombre = nuevo_nombre
        self.evento_en_edicion_actual.fecha = nueva_fecha
        self.evento_en_edicion_actual.ubicacion = nueva_ubicacion
        self.evento_en_edicion_actual.organizador = nuevo_organizador

        # Si cambias el número de mesas
        if self.evento_en_edicion_actual.numMesas != nuevo_numMesas:
            # Cambia el num de mesas
            self.evento_en_edicion_actual.numMesas = nuevo_numMesas
            # Borra las mesas viejas
            self.evento_en_edicion_actual.mesas = []
            capacidad_por_mesa = 10 # Pone la capacidad por defecto
            # Y crea las nuevas vacías
            for i in range(nuevo_numMesas):
                id_mesa = f"{self.evento_en_edicion_actual.IdEvento}_mesa_{i+1}"
                nueva_mesa = Mesa(id_mesa=id_mesa, numero=i+1, capacidad=capacidad_por_mesa)
                self.evento_en_edicion_actual.mesas.append(nueva_mesa)
            QMessageBox.warning(self,"Oye", "Se restauraron las mesas tendras que asignar de nuevo")       

        # Guarda en json
        self.gestor_datos.guardarEventos(self.lista_eventos)
        # Limpia el evento actual
        self.evento_en_edicion_actual = None
        # Vuelve al crud
        self.mostrar_pagina_crud()


    def borrar_evento_seleccionado(self):

        # Pilla la tabla borrar
        tabla_borrar = self.pagina_borrar.ui.EventList_Table_Delete
        
        # Pilla la fila seleccionada
        fila_seleccionada = tabla_borrar.currentRow()

        # Si no hay fila te avisa
        if fila_seleccionada == -1:
            QMessageBox.warning(self, "Oye", "No has seleccionado ningun evento.")
            return

        # Pilla el evento de la lista
        try:
            evento_a_borrar = self.lista_eventos[fila_seleccionada]
            nombre_evento = evento_a_borrar.nombre
        except IndexError:
            QMessageBox.critical(self, "Error", "no se ha podido borrar")
            return

        # Te pregunta si estás seguro
        confirmacion = QMessageBox.question(
            self,
            "Confirmar borrado",
            f"¿Estás seguro de que quieres borrar el evento '{nombre_evento}'?\n\nEsta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No # No por defecto
        )

        # Si dices que sí
        if confirmacion == QMessageBox.Yes:
            # Lo borra de la lista
            self.lista_eventos.pop(fila_seleccionada)
            
            # Guarda en el json
            self.gestor_datos.guardarEventos(self.lista_eventos)
            
            # Recarga la tabla de borrar
            self.actualizar_tabla_borrar()

            # Vuelve al menu
            self.mostrar_pagina_crud()
            
        else:
            # No hace nada
            return

    # Carga los eventos del JSON
    # Y refresca la tabla principal
    def cargar_y_actualizar_eventos(self):
        self.lista_eventos = self.gestor_datos.cargarEventos()
        self.actualizar_tabla_crud()

    # Carga los eventos del JSON
    # Y refresca la tabla de borrar
    def cargar_y_actualizar_eventos_borrar(self):
        self.lista_eventos = self.gestor_datos.cargarEventos()
        self.actualizar_tabla_borrar()

# Guarda un evento desde la página 1
# Si no se usó la página de invitados
    def guardar_nuevo_evento(self):
        # Pilla los datos de los campos
        nombre = self.pagina_crear.ui.Input_EventName.text()
        fecha = self.pagina_crear.ui.Input_EventDate.text()
        ubicacion = self.pagina_crear.ui.Input_EventLocation.text()
        organizador = self.pagina_crear.ui.Input_EventOrganizer.text()
        numMesas = self.pagina_crear.ui.Input_NumTables.value()

        # Si falta nombre o fecha te avisa
        if not nombre or not fecha:
            QMessageBox.warning(self,  "Oye", "Pon el nombre y la fecha")       
            return
            
        # Mira si ya hay un evento temporal
        # (Hecho desde el CSV o manual)
        if self.evento_en_edicion_actual and self.evento_en_edicion_actual.nombre == nombre:
            nuevo_evento = self.evento_en_edicion_actual
            # Actualizamos por si acaso
            nuevo_evento.fecha = fecha
            nuevo_evento.ubicacion = ubicacion
            nuevo_evento.organizador = organizador
            nuevo_evento.numMesas = numMesas
        else:
        # Si no hay evento temporal
        # Crea uno nuevo
            # Crea el id
            nuevo_id = f"evento_{len(self.lista_eventos) + 1}"

            # Crea el evento
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

        # Añade el evento a la lista
        self.lista_eventos.append(nuevo_evento)

        # Guarda la lista
        self.gestor_datos.guardarEventos(self.lista_eventos)


        # Vacia los text field
        self.pagina_crear.ui.Input_EventName.setText("")
        self.pagina_crear.ui.Input_EventDate.setText("")
        self.pagina_crear.ui.Input_EventLocation.setText("")
        self.pagina_crear.ui.Input_EventOrganizer.setText("")
        self.pagina_crear.ui.Input_NumTables.setValue(1)
        
        # Limpia las variables
        self.evento_en_edicion_actual = None
        self.participante_en_gestion = None
        self.pagina_participantes.ui.Input_ParticipantName.setText("")
        self.actualizar_listas_participantes()

        # Vuelve al menu
        self.mostrar_pagina_crud()

    def actualizar_tabla_crud(self):

        # Pilla la tabla
        tabla = self.pagina_crud.ui.EventList_Table
        
        # Bloquea señales para que no pete
        tabla.blockSignals(True)
        
        # Limpia la tabla
        tabla.setRowCount(0) 
        
        # Recorre los eventos
        for evento in self.lista_eventos:
            # Pilla la posicion
            row_position = tabla.rowCount()
            # Mete una fila nueva
            tabla.insertRow(row_position)
            
            # Rellena las celdas
            tabla.setItem(row_position, 0, QTableWidgetItem(evento.nombre))
            tabla.setItem(row_position, 1, QTableWidgetItem(evento.fecha))
            tabla.setItem(row_position, 2, QTableWidgetItem(evento.ubicacion))
            tabla.setItem(row_position, 3, QTableWidgetItem(evento.organizador))
            
        # Desbloquea las señales
        tabla.blockSignals(False)
        
        # Ajusta el ancho de columnas
        tabla.resizeColumnsToContents()

    def actualizar_tabla_borrar(self):
        # Refresca la tabla de borrar
        # Igual que la de crud
        tabla = self.pagina_borrar.ui.EventList_Table_Delete
        tabla.blockSignals(True)
        tabla.setRowCount(0)
         # Recorre los eventos
        for evento in self.lista_eventos:
            # Pilla la posicion
            row_position = tabla.rowCount()
            # Mete una fila nueva
            tabla.insertRow(row_position)

            # Rellena las celdas
            tabla.setItem(row_position, 0, QTableWidgetItem(evento.nombre))
            tabla.setItem(row_position, 1, QTableWidgetItem(evento.fecha))
            tabla.setItem(row_position, 2, QTableWidgetItem(evento.ubicacion))
            tabla.setItem(row_position, 3, QTableWidgetItem(evento.organizador))
            
        tabla.blockSignals(False) # Faltaba esto

    # --- Funciones de CSV antiguas eliminadas ---
    # (Eran para pandas y no estaban conectadas)

    def mostrar_pagina_auto(self):
        self.setCurrentIndex(7)

    # Enseña la pantalla de excepciones
    def mostrar_pagina_excepciones(self):
        if self.evento_en_edicion_actual is None:
            return
            
        self.excepcion_mesa_actual_idx = 0 # Empieza en la mesa 0
        self.actualizar_listas_excepciones_ui()
        self.setCurrentIndex(8)

    # El algoritmo mágico de Google
    def algoritmo_asignar_mesas(self, participantes, mesas):
        
        # 0. Si no hay mesas o invitados se pira
        excepciones = []
        if not mesas:
            print("Error: No hay mesas para asignar.")
            return participantes  # Todos son excepciones
        
        if not participantes:
            print("No hay participantes para asignar.")
            return [] # No hay excepciones

        # 1. Mapas para pillar nombres e IDs
        nombre_a_obj = {p.nombre: p for p in participantes}
        
        # 2. Crea el modelo
        model = cp_model.CpModel()

        # 3. Crea las variables
        # Cada invitado tendrá un número (el de su mesa)
        participante_vars = {
            p.id_participante: model.NewIntVar(0, len(mesas) - 1, p.nombre)
            for p in participantes
        }

        # 4. Pone las reglas
        # 4a. Regla: Capacidad de la mesa
        for i, mesa in enumerate(mesas):
            # Mira cuántos invitados tienen el número 'i'
            indicadores = []
            for p in participantes:
                p_id = p.id_participante
                # 'b' es Verdad si el invitado 'p' está en la mesa 'i'
                b = model.NewBoolVar(f"{p_id}_en_mesa_{i}")
                model.Add(participante_vars[p_id] == i).OnlyEnforceIf(b)
                model.Add(participante_vars[p_id] != i).OnlyEnforceIf(b.Not())
                indicadores.append(b)
            
            # La suma de invitados no puede ser mayor a la capacidad
            model.Add(sum(indicadores) <= mesa.capacidad)

        # 4b. Regla: Amigos (Preferencias)
        preferencias_procesadas = set()
        for p in participantes:
            var_p = participante_vars[p.id_participante]
            for amigo_nombre in p.preferencias:
                
                # Si el amigo existe y no hemos hecho ya esta pareja
                if amigo_nombre in nombre_a_obj and (amigo_nombre, p.nombre) not in preferencias_procesadas:
                    amigo_obj = nombre_a_obj[amigo_nombre]
                    var_amigo = participante_vars[amigo_obj.id_participante]
                    
                    # Obliga a que sus números de mesa sean iguales
                    model.Add(var_p == var_amigo)
                    preferencias_procesadas.add((p.nombre, amigo_nombre))

        # 4c. Regla: Enemigos (Evitados)
        for p in participantes:
            var_p = participante_vars[p.id_participante]
            for enemigo_nombre in p.evitados:
                
                if enemigo_nombre in nombre_a_obj:
                    enemigo_obj = nombre_a_obj[enemigo_nombre]
                    var_enemigo = participante_vars[enemigo_obj.id_participante]
                    
                    # Obliga a que sus números de mesa sean DIFERENTES
                    model.Add(var_p != var_enemigo)

        # 5. Resuelve el puzzle
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        # 6. Reparte los resultados
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print("Asignación automática completada (OR-Tools).")
            
            # Reparte a los invitados en las mesas
            for p in participantes:
                id_mesa_asignada = solver.Value(participante_vars[p.id_participante])
                mesa_obj = mesas[id_mesa_asignada]
                
                # Añade el invitado a la mesa (objeto)
                mesa_obj.anadirParticipante(p)
                # Y le dice al invitado dónde está
                p.asignar_mesa(mesa_obj.id_mesa)
            
            # Si todo fue bien no hay excepciones
            return [] 
            
        else:
            # Si el puzzle no tiene solución
            print("No se encontró solución factible con OR-Tools.")
            QMessageBox.warning(self, "Conflicto de Asignación", 
                                "No se pudo encontrar una solución que respete todas las reglas (preferencias/evitados).\n\n"
                                "Revisa las restricciones o usa la asignación manual.")
            
            # Devuelve a todos como excepciones
            return participantes


    def ejecutar_asignacion_automatica(self):
        # Si no hay evento te echa
        if self.evento_en_edicion_actual is None:
            QMessageBox.critical(self, "Error")
            return

        print(f"Iniciando asignación automática para: {self.evento_en_edicion_actual.nombre}")

        # Vacía las mesas
        for mesa in self.evento_en_edicion_actual.mesas:
            mesa.participantes = []

        # Les quita la mesa a todos los invitados
        for p in self.evento_en_edicion_actual.participantes:
            p.quitar_mesa()

        # Prepara las listas para el algoritmo
        participantes_a_asignar = list(self.evento_en_edicion_actual.participantes)
        mesas_del_evento = list(self.evento_en_edicion_actual.mesas)

        # Llama al algoritmo
        self.lista_excepciones = self.algoritmo_asignar_mesas(participantes_a_asignar, mesas_del_evento)

        # Guarda en el JSON
        self.gestor_datos.guardarEventos(self.lista_eventos)

        # Actualiza las tablas
        self.actualizar_tabla_resultados_auto()
        self.actualizar_lista_excepciones()

        # Enseña la página de resultados
        self.mostrar_pagina_auto()


    def actualizar_tabla_resultados_auto(self):
        # Refresca la tabla de resultados automáticos
        tabla = self.pagina_resultados_auto.ui.Results_Table
        tabla.blockSignals(True)
        tabla.setRowCount(0)

        if self.evento_en_edicion_actual:
            # Rellena mesa por mesa
            for mesa in self.evento_en_edicion_actual.mesas:
                row_position = tabla.rowCount()
                tabla.insertRow(row_position)

                # Pone "Mesa 1 (5/10)"
                texto_mesa = f"Mesa {mesa.numero} ({len(mesa.participantes)}/{mesa.capacidad})"
                tabla.setItem(row_position, 0, QTableWidgetItem(texto_mesa))

                # Pone "Ana Jose Juan..."
                nombres = [p.nombre for p in mesa.participantes]
                texto_nombres = ", ".join(nombres)
                tabla.setItem(row_position, 1, QTableWidgetItem(texto_nombres))

        tabla.blockSignals(False)
        # Ajusta el ancho de las columnas
        tabla.resizeColumnsToContents()


    def actualizar_lista_excepciones(self):
        # Refresca la lista de excepciones
        lista = self.pagina_excepciones.ui.List_Exceptions
        lista.clear()

        for participante in self.lista_excepciones:
            lista.addItem(participante.nombre)

    # Función ayudante
    # Crea un evento temporal
    # No lo guarda aún
    def _crear_evento_temporal_desde_pagina1(self):
        # Pilla los datos de la página 1
        nombre = self.pagina_crear.ui.Input_EventName.text().strip()
        fecha = self.pagina_crear.ui.Input_EventDate.text().strip()
        
        # Si faltan datos avisa y devuelve Falso
        if not nombre or not fecha:
            QMessageBox.warning(self, "Datos incompletos", 
                            "Debes completar al menos el Nombre y la Fecha del evento antes de cargar participantes.")
            return False
        
        ubicacion = self.pagina_crear.ui.Input_EventLocation.text().strip()
        organizador = self.pagina_crear.ui.Input_EventOrganizer.text().strip()
        numMesas = self.pagina_crear.ui.Input_NumTables.value()
        nuevo_id = f"evento_{len(self.lista_eventos) + 1}"
        
        # Crea el objeto y lo guarda en la variable temporal
        try:
            self.evento_en_edicion_actual = Evento(
                IdEvento=nuevo_id,
                nombre=nombre,
                fecha=fecha,
                ubicacion=ubicacion,
                organizador=organizador,
                numMesas=numMesas
            )
            return True # Devuelve Verdadero si todo OK
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo crear el evento temporal.\n{e}")
            return False
    
    def cargar_participantes_csv(self):
        # Carga invitados desde un archivo CSV
        pagina_actual = self.currentIndex()

        # 1. Mira si tenemos un evento listo
        if pagina_actual == 1: # Si estás en "Crear"
            # Si no hay evento temporal
            if self.evento_en_edicion_actual is None:
                # Intenta crearlo
                if not self._crear_evento_temporal_desde_pagina1():
                    return # Si falla se pira
        
        elif pagina_actual == 2: # Si estás en "Actualizar"
            if self.evento_en_edicion_actual is None:
                QMessageBox.critical(self, "Error", "No hay evento seleccionado (esto no debería pasar)")
                return
        
        # 2. Abre la ventana para buscar archivo
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(self, "Seleccionar CSV de Participantes", "", "Archivos CSV (*.csv);;Todos los archivos (*)", options=options)

        # Si cancelas se pira
        if not filePath:
            return

        # 3. Lee el archivo CSV
        try:
            participantes_cargados = 0
            with open(filePath, mode='r', encoding='utf-8') as f:
                # Lee la primera fila como cabeceras
                reader = csv.DictReader(f)
                
                # Lee fila por fila
                for row in reader:
                    # Pilla el nombre (con mayús o minús)
                    nombre_participante = row.get('Nombre') or row.get('nombre')
                    
                    # Si no hay nombre pasa a la siguiente fila
                    if not nombre_participante:
                        continue
                        
                    # Crea el ID del invitado
                    evento_id = self.evento_en_edicion_actual.IdEvento
                    num_part = len(self.evento_en_edicion_actual.participantes)
                    participante_id = f"{evento_id}_p_{num_part + 1}"
                    
                    # Crea el objeto Participante
                    nuevo_participante = Participante(participante_id, nombre_participante)

                    # Pilla las preferencias
                    pref_texto = row.get('Preferencias') or row.get('preferencias', '')
                    if pref_texto:
                        # Las corta por ";"
                        lista_pref = [nombre.strip() for nombre in pref_texto.split(';') if nombre.strip()]
                        nuevo_participante.preferencias = lista_pref

                    # Pilla los evitados
                    evit_texto = row.get('Evitados') or row.get('evitados', '')
                    if evit_texto:
                        # Las corta por ";"
                        lista_evit = [nombre.strip() for nombre in evit_texto.split(';') if nombre.strip()]
                        nuevo_participante.evitados = lista_evit
                    
                    # Añade el invitado al evento
                    self.evento_en_edicion_actual.anadirparticipante(nuevo_participante)
                    participantes_cargados += 1

            # Te avisa cuántos ha cargado
            QMessageBox.information(self, "Éxito", f"Se han cargado {participantes_cargados} participantes desde el CSV.")
            
            # Si estabas en "Actualizar"
            # Guarda en el JSON al momento
            if pagina_actual == 2:
                self.gestor_datos.guardarEventos(self.lista_eventos)

        except Exception as e:
            # Si algo peta te avisa
            QMessageBox.critical(self, "Error al leer CSV", f"No se pudo leer el archivo.\nError: {e}")

    
    # --- Lógica para Asignación Manual (Página 4) ---

    def actualizar_listas_manual(self):
        # Refresca las listas de la página manual
        if not self.evento_en_edicion_actual or not self.evento_en_edicion_actual.mesas:
            return

        # 1. Pilla la mesa que toca ver
        mesa_actual = self.evento_en_edicion_actual.mesas[self.mesa_manual_actual_idx]
        # Pone el título "Mesa 1 (3/10)"
        self.pagina_manual.ui.Label_TableParticipants.setText(f"Mesa {mesa_actual.numero} ({len(mesa_actual.participantes)}/{mesa_actual.capacidad})")

        # 2. Limpia la lista de la mesa
        lista_mesa_ui = self.pagina_manual.ui.List_TableParticipants
        lista_mesa_ui.clear()
        # Mete los invitados de esa mesa
        for p in mesa_actual.participantes:
            lista_mesa_ui.addItem(p.nombre)

        # 3. Limpia la lista de "Sin Asignar"
        lista_sin_asignar_ui = self.pagina_manual.ui.List_UnassignedGuests
        lista_sin_asignar_ui.clear()
        
        # Crea una lista de todos los que YA tienen mesa
        participantes_asignados_ids = set()
        for m in self.evento_en_edicion_actual.mesas:
            for p in m.participantes:
                participantes_asignados_ids.add(p.id_participante)

        # Recorre TODOS los invitados del evento
        for p in self.evento_en_edicion_actual.participantes:
            # Si el invitado NO está en la lista de asignados
            if p.id_participante not in participantes_asignados_ids:
                # Lo mete en la lista "Sin Asignar"
                lista_sin_asignar_ui.addItem(p.nombre)

    def manual_siguiente_mesa(self):
        # Botón flecha derecha de mesa manual
        if not self.evento_en_edicion_actual: return
        num_mesas = len(self.evento_en_edicion_actual.mesas)
        if num_mesas > 0:
            # Suma 1 al índice de la mesa
            self.mesa_manual_actual_idx = (self.mesa_manual_actual_idx + 1) % num_mesas
            # Y recarga las listas
            self.actualizar_listas_manual()

    def manual_anterior_mesa(self):
        # Botón flecha izquierda de mesa manual
        if not self.evento_en_edicion_actual: return
        num_mesas = len(self.evento_en_edicion_actual.mesas)
        if num_mesas > 0:
            # Resta 1 al índice de la mesa
            self.mesa_manual_actual_idx = (self.mesa_manual_actual_idx - 1) % num_mesas
            # Y recarga las listas
            self.actualizar_listas_manual()

    def manual_anadir_participante(self):
        # Botón "Añadir" en mesa manual
        # Pilla el invitado de la lista "Sin Asignar"
        item_seleccionado = self.pagina_manual.ui.List_UnassignedGuests.currentItem()
        if not item_seleccionado or not self.evento_en_edicion_actual:
            return

        # Pilla la mesa actual
        mesa_actual = self.evento_en_edicion_actual.mesas[self.mesa_manual_actual_idx]
        # Si está llena te avisa
        if mesa_actual.estaLlena():
            QMessageBox.warning(self, "Mesa Llena", f"La Mesa {mesa_actual.numero} ya está llena.")
            return

        # Busca el objeto invitado por su nombre
        nombre_p = item_seleccionado.text()
        participante_a_mover = None
        
        # Busca al participante que tenga ese nombre Y NO esté asignado
        participantes_asignados_ids = set()
        for m in self.evento_en_edicion_actual.mesas:
            for p in m.participantes:
                participantes_asignados_ids.add(p.id_participante)
        
        for p in self.evento_en_edicion_actual.participantes:
            if p.nombre == nombre_p and p.id_participante not in participantes_asignados_ids:
                participante_a_mover = p
                break
        
        # Si lo encuentra...
        if participante_a_mover:
            # Lo mete en la mesa
            mesa_actual.anadirParticipante(participante_a_mover)
            # Le dice al invitado a qué mesa va
            participante_a_mover.asignar_mesa(mesa_actual.id_mesa)
            # Recarga las listas
            self.actualizar_listas_manual()
            # Guarda en el JSON
            self.gestor_datos.guardarEventos(self.lista_eventos)

    def manual_eliminar_participante(self):
        # Botón "Eliminar" en mesa manual
        # Pilla el invitado de la lista "Participantes en Mesa"
        item_seleccionado = self.pagina_manual.ui.List_TableParticipants.currentItem()
        if not item_seleccionado or not self.evento_en_edicion_actual:
            return

        mesa_actual = self.evento_en_edicion_actual.mesas[self.mesa_manual_actual_idx]
        
        # Busca el objeto invitado
        nombre_p = item_seleccionado.text()
        participante_a_mover = None
        for p in mesa_actual.participantes:
            if p.nombre == nombre_p:
                participante_a_mover = p
                break

        if participante_a_mover:
            # Lo saca de la mesa
            mesa_actual.eliminarParticipante(participante_a_mover)
            # Le dice al invitado que ya no tiene mesa
            participante_a_mover.quitar_mesa()
            # Recarga las listas
            self.actualizar_listas_manual()
            # Guarda en el JSON
            self.gestor_datos.guardarEventos(self.lista_eventos)

    # --- Lógica para Gestión de Participantes (Página 6) ---

    # Se activa cuando el usuario escribe en el QLineEdit
    def limpiar_participante_en_gestion(self, texto):
        # Si el usuario escribe
        # Asumimos que quiere crear uno nuevo
        # Así que limpiamos la selección
        if self.participante_en_gestion and texto != self.participante_en_gestion.nombre:
            self.participante_en_gestion = None
            self.pagina_participantes.ui.List_AllGuests.clearSelection()
            self.actualizar_listas_preferencias()

    # Se activa al hacer DOBLE CLIC en un invitado
    def gestionar_participante_seleccionado(self, item):
        # Carga a este participante para editarlo
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
                    self.participante_en_gestion = p
                    break
        
        if self.participante_en_gestion:
            # Pone su nombre en el campo de texto
            self.pagina_participantes.ui.Input_ParticipantName.setText(self.participante_en_gestion.nombre)
            # Carga sus listas de prefs y evitados
            self.actualizar_listas_preferencias()

    def actualizar_listas_preferencias(self):
        # Refresca las listas de Preferencia y Evitados
        lista_pref = self.pagina_participantes.ui.List_Preference
        lista_evit = self.pagina_participantes.ui.List_Avoid
        
        # Limpia las dos listas
        lista_pref.clear()
        lista_evit.clear()

        # Si hay un invitado "en gestión"
        if self.participante_en_gestion:
            # Rellena las listas
            for nombre_pref in self.participante_en_gestion.preferencias:
                lista_pref.addItem(nombre_pref)
            for nombre_evit in self.participante_en_gestion.evitados:
                lista_evit.addItem(nombre_evit)

    # Botón verde (V)
    def participante_anadir_preferencia(self):
        # Pone al invitado seleccionado (1 clic)
        # en las preferencias del invitado "en gestión" (doble clic o recién añadido)
        if not self.participante_en_gestion:
            QMessageBox.warning(self, "Error", "Primero añade o selecciona (con doble clic) un participante (ej: 'Asa') para editarlo.")
            return

        # Pilla el invitado con UN clic en "Todos los Invitados"
        item_seleccionado = self.pagina_participantes.ui.List_AllGuests.currentItem()
        if not item_seleccionado:
            QMessageBox.warning(self, "Error", "Ahora, selecciona (con un solo clic) a *otro* participante (ej: 'Pepica') para añadir a sus preferencias.")
            return
            
        nombre_a_anadir = item_seleccionado.text()

        # No puedes añadirte a ti mismo
        if nombre_a_anadir == self.participante_en_gestion.nombre:
            QMessageBox.warning(self, "Error", "No puedes añadir a un participante a sus propias preferencias.")
            return
            
        # Añade el nombre a la lista de preferencias
        if self.participante_en_gestion.anadir_preferencia(nombre_a_anadir):
            # Lo quita de evitados (por si acaso)
            self.participante_en_gestion.eliminar_evitado(nombre_a_anadir)
            self.actualizar_listas_preferencias() # Recarga las listas
            
            # Si estás actualizando guarda en JSON
            if self.modo_gestion_participantes == "ACTUALIZAR":
                self.gestor_datos.guardarEventos(self.lista_eventos)

    # Botón rojo (X)
    def participante_anadir_evitado(self):
        # Pone al invitado seleccionado (1 clic)
        # en los evitados del invitado "en gestión"
        if not self.participante_en_gestion:
            QMessageBox.warning(self, "Error", "Primero añade o selecciona (con doble clic) un participante (ej: 'Asa') para editarlo.")
            return

        # Pilla el invitado con UN clic
        item_seleccionado = self.pagina_participantes.ui.List_AllGuests.currentItem()
        if not item_seleccionado:
            QMessageBox.warning(self, "Error", "Ahora, selecciona (con un solo clic) a *otro* participante (ej: 'Pepica') para añadir a sus evitados.")
            return

        nombre_a_anadir = item_seleccionado.text()

        # No puedes evitarte a ti mismo
        if nombre_a_anadir == self.participante_en_gestion.nombre:
            QMessageBox.warning(self, "Error", "No puedes añadir a un participante a su propia lista de evitados.")
            return

        # Añade el nombre a la lista de evitados
        if self.participante_en_gestion.anadir_evitado(nombre_a_anadir):
            # Lo quita de preferencias (por si acaso)
            self.participante_en_gestion.eliminar_preferencia(nombre_a_anadir)
            self.actualizar_listas_preferencias() # Recarga las listas
            
            # Si estás actualizando guarda en JSON
            if self.modo_gestion_participantes == "ACTUALIZAR":
                self.gestor_datos.guardarEventos(self.lista_eventos)

    def participante_eliminar_relacion(self):
        # Botón "Eliminar" en Pág 6
        if not self.participante_en_gestion:
            QMessageBox.warning(self, "Error", "No hay ningún participante seleccionado para editar.")
            return

        # Mira si has seleccionado a alguien en "Preferencia"
        item_pref = self.pagina_participantes.ui.List_Preference.currentItem()
        if item_pref:
            # Si es así lo borra de la lista de preferencias
            self.participante_en_gestion.eliminar_preferencia(item_pref.text())
            self.actualizar_listas_preferencias()
            return

        # Mira si has seleccionado a alguien en "No acepta"
        item_evit = self.pagina_participantes.ui.List_Avoid.currentItem()
        if item_evit:
            # Si es así lo borra de la lista de evitados
            self.participante_en_gestion.eliminar_evitado(item_evit.text())
            self.actualizar_listas_preferencias()
            return

    # --- Lógica para Gestión de Excepciones (Página 8) ---
    
    def actualizar_listas_excepciones_ui(self):
        # Refresca las listas de la Pág 8 (Excepciones)
        if not self.evento_en_edicion_actual or not self.evento_en_edicion_actual.mesas:
            return

        # 1. Pilla la mesa que toca
        mesa_actual = self.evento_en_edicion_actual.mesas[self.excepcion_mesa_actual_idx]
        self.pagina_excepciones.ui.Label_TableParticipants.setText(f"Mesa {mesa_actual.numero} ({len(mesa_actual.participantes)}/{mesa_actual.capacidad})")

        # 2. Limpia y rellena la lista de la mesa
        lista_mesa_ui = self.pagina_excepciones.ui.List_TableParticipants
        lista_mesa_ui.clear()
        for p in mesa_actual.participantes:
            lista_mesa_ui.addItem(p.nombre)

        # 3. Limpia y rellena la lista de "Conflictos"
        lista_excepciones_ui = self.pagina_excepciones.ui.List_Exceptions
        lista_excepciones_ui.clear()
        # Rellena con los invitados que el algoritmo no pudo sentar
        for p in self.lista_excepciones:
            lista_excepciones_ui.addItem(p.nombre)

    def excepcion_siguiente_mesa(self):
        # Botón flecha derecha de excepciones
        if not self.evento_en_edicion_actual: return
        num_mesas = len(self.evento_en_edicion_actual.mesas)
        if num_mesas > 0:
            self.excepcion_mesa_actual_idx = (self.excepcion_mesa_actual_idx + 1) % num_mesas
            self.actualizar_listas_excepciones_ui()

    def excepcion_anterior_mesa(self):
        # Botón flecha izquierda de excepciones
        if not self.evento_en_edicion_actual: return
        num_mesas = len(self.evento_en_edicion_actual.mesas)
        if num_mesas > 0:
            self.excepcion_mesa_actual_idx = (self.excepcion_mesa_actual_idx - 1) % num_mesas
            self.actualizar_listas_excepciones_ui()

    def excepcion_anadir_participante(self):
        # Botón "Añadir" en excepciones
        # Pilla el invitado de la lista "Conflictos"
        item_seleccionado = self.pagina_excepciones.ui.List_Exceptions.currentItem()
        if not item_seleccionado or not self.evento_en_edicion_actual:
            return

        mesa_actual = self.evento_en_edicion_actual.mesas[self.excepcion_mesa_actual_idx]
        # Si la mesa está llena te avisa
        if mesa_actual.estaLlena():
            QMessageBox.warning(self, "Mesa Llena", f"La Mesa {mesa_actual.numero} ya está llena.")
            return

        # Busca el objeto invitado
        nombre_p = item_seleccionado.text()
        participante_a_mover = None
        for p in self.lista_excepciones:
            if p.nombre == nombre_p:
                participante_a_mover = p
                break
        
        if participante_a_mover:
            # Lo mete en la mesa
            mesa_actual.anadirParticipante(participante_a_mover)
            participante_a_mover.asignar_mesa(mesa_actual.id_mesa)
            # Lo quita de la lista de "Conflictos"
            self.lista_excepciones.remove(participante_a_mover) 
            self.actualizar_listas_excepciones_ui()
            self.gestor_datos.guardarEventos(self.lista_eventos) # Guarda en JSON

    def excepcion_eliminar_participante(self):
        # Botón "Eliminar" en excepciones
        # Pilla el invitado de la lista "Participantes en Mesa"
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
            # Lo saca de la mesa
            mesa_actual.eliminarParticipante(participante_a_mover)
            participante_a_mover.quitar_mesa()
            # Lo devuelve a la lista de "Conflictos"
            self.lista_excepciones.append(participante_a_mover) 
            self.actualizar_listas_excepciones_ui()
            self.gestor_datos.guardarEventos(self.lista_eventos) # Guarda en JSON

    # --- Lógica para Generar CSV (Página 0) ---
    
    # Botón "Abrir Ruta de CSV"
    def abrir_carpeta_csvs(self):
        # Crea la carpeta "CSVs_Generados" si no existe
        os.makedirs(self.CSV_EXPORT_PATH, exist_ok=True)
        
        # Abre esa carpeta en el explorador de archivos
        try:
            webbrowser.open(os.path.realpath(self.CSV_EXPORT_PATH))
            QMessageBox.information(self, "Carpeta Abierta",
                                  f"Se ha abierto la carpeta:\n{os.path.realpath(self.CSV_EXPORT_PATH)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir la carpeta.\nError: {e}")

    # Botón "Generar CSV"
    def generar_csv_evento_seleccionado(self):
        # Genera un CSV con toda la info del evento
        # Y lo guarda en 'CSVs_Generados'
        tabla_crud = self.pagina_crud.ui.EventList_Table
        fila_seleccionada = tabla_crud.currentRow()

        # Si no hay evento seleccionado te avisa
        if fila_seleccionada == -1:
            QMessageBox.warning(self, "Error", "Selecciona un evento para generar el CSV.")
            return

        try:
            evento_seleccionado = self.lista_eventos[fila_seleccionada]
        except IndexError:
            QMessageBox.critical(self, "Error", "Error al obtener el evento.")
            return

        # 1. Crea la carpeta si no existe
        os.makedirs(self.CSV_EXPORT_PATH, exist_ok=True)
        
        # 2. Limpia el nombre del evento
        nombre_base = "".join(c for c in evento_seleccionado.nombre if c.isalnum() or c in (' ', '_')).rstrip()
        nombre_archivo = f"{nombre_base.replace(' ', '_')}_completo.csv"
        filePath = os.path.join(self.CSV_EXPORT_PATH, nombre_archivo)

        try:
            # 3. Abre el archivo para escribir
            with open(filePath, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                
                # Escribe la info del evento
                writer.writerow(["--- INFORMACIÓN DEL EVENTO ---"])
                writer.writerow(["ID Evento", evento_seleccionado.IdEvento])
                writer.writerow(["Nombre", evento_seleccionado.nombre])
                writer.writerow(["Fecha", evento_seleccionado.fecha])
                writer.writerow(["Ubicacion", evento_seleccionado.ubicacion])
                writer.writerow(["Organizador", evento_seleccionado.organizador])
                writer.writerow(["", ""]) # Línea vacía
                
                # Escribe la info de los participantes
                writer.writerow(["--- LISTA DE PARTICIPANTES ---"])
                writer.writerow(["Nombre", "ID Participante", "Preferencias (Nombres)", "Evitados (Nombres)", "Mesa Asignada (ID)"])
                for p in evento_seleccionado.participantes:
                    preferencias_str = "; ".join(p.preferencias)
                    evitados_str = "; ".join(p.evitados)
                    
                    # Busca el número de la mesa asignada
                    nombre_mesa = "Sin Asignar"
                    if p.mesa_asignada:
                        for m in evento_seleccionado.mesas:
                            if m.id_mesa == p.mesa_asignada:
                                nombre_mesa = f"Mesa {m.numero}"
                                break
                                
                    writer.writerow([p.nombre, p.id_participante, preferencias_str, evitados_str, nombre_mesa])
                writer.writerow(["", ""]) # Línea vacía

                # Escribe la info de las mesas
                writer.writerow(["--- ASIGNACIÓN DE MESAS ---"])
                for m in evento_seleccionado.mesas:
                    writer.writerow([f"Mesa {m.numero}", f"ID: {m.id_mesa}", f"Capacidad: ({len(m.participantes)} / {m.capacidad})"])
                    
                    # Escribe los nombres de los que están en esa mesa
                    nombres_en_mesa = [p.nombre for p in m.participantes]
                    if nombres_en_mesa:
                        writer.writerow([""] + nombres_en_mesa) 
                    else:
                        writer.writerow(["", "(Mesa Vacía)"])
                    writer.writerow(["", ""]) # Línea vacía
            
            # Te avisa que lo ha guardado
            QMessageBox.information(self, "Éxito", f"CSV completo generado exitosamente en:\n{os.path.realpath(filePath)}")

        except Exception as e:
            QMessageBox.critical(self, "Error al escribir CSV", f"No se pudo guardar el archivo.\nError: {e}")


# El arranque
if __name__ == "__main__":
    # Crea la app
    app = QApplication(sys.argv)
    # Crea la ventana principal
    ventana = VentanaPrincipal()
    # La enseña
    ventana.show()
    # Y la mantiene abierta
    sys.exit(app.exec_())