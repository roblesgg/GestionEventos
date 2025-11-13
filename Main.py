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
        self.pagina_mesas.ui.AutoAssign_Btn.clicked.connect(self.mostrar_pagina_auto)
        self.pagina_resultados_auto.ui.ViewExceptions_Btn.clicked.connect(self.mostrar_pagina_excepciones)

        #botones de otras pestañas
        self.pagina_mesas.ui.ManualAssign_Btn.clicked.connect(self.mostrar_pagina_manual)
        self.pagina_crear.ui.CreateManual_Btn.clicked.connect(self.preparar_evento_para_participantes)
        self.pagina_crud.ui.OpenCSVPath_Btn.clicked.connect(self.seleccionar_csv)
        self.pagina_crear.ui.UploadCSV_Btn.clicked.connect(self.cargar_participantes_csv)
        self.pagina_actualizar.ui.UploadCSV_Btn.clicked.connect(self.cargar_participantes_csv)

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
        
        # Boton atras de añadir participantes manualmemnte
        self.pagina_participantes.ui.BackButton_Participants.clicked.connect(self.mostrar_pagina_crear)
        
        # Botonañadir
        self.pagina_participantes.ui.Add_Btn.clicked.connect(self.anadir_participante_al_evento)
        
        # Boton finalizar que guarda
        self.pagina_participantes.ui.Finish_Btn.clicked.connect(self.guardar_evento_y_participantes)

        # Botón atrás de añadir
        self.pagina_manual.ui.BackButton_ManualAssign.clicked.connect(self.mostrar_pagina_mesas)

        # Botón atrás de automático 
        self.pagina_resultados_auto.ui.BackButton_AutoAssign.clicked.connect(self.mostrar_pagina_mesas)

        # Botón atrás excepciones
        self.pagina_excepciones.ui.BackButton_Exceptions.clicked.connect(self.mostrar_pagina_auto)
        
        #la pestaña inicial
        self.resize(904, 617)
        #pone los eventos del csv
        self.cargar_y_actualizar_eventos()


    #metodos de cambiar de pagina
    def mostrar_pagina_crud(self):
        self.actualizar_tabla_crud()
        self.setCurrentIndex(0)
        
    def mostrar_pagina_crear(self):
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

    def mostrar_pagina_manual(self):
        self.setCurrentIndex(4)

    def mostrar_pagina_borrar(self):
        self.setCurrentIndex(5)
        self.cargar_y_actualizar_eventos_borrar()
    


    #mas metodos varios

    def preparar_evento_para_participantes(self):
        #coge las variables de el evento
        nombre = self.pagina_crear.ui.Input_EventName.text()
        fecha = self.pagina_crear.ui.Input_EventDate.text()
        
        #comprueba que esten nombre y fecha
        if not nombre or not fecha:
            QMessageBox.warning(self, "Oye", "Pon el nombre y la fecha antes de añadir participantes")       
            return #sale

        #coge todos los datos quefaltan
        ubicacion = self.pagina_crear.ui.Input_EventLocation.text()
        organizador = self.pagina_crear.ui.Input_EventOrganizer.text()
        numMesas = self.pagina_crear.ui.Input_NumTables.value()
        nuevo_id = f"evento_{len(self.lista_eventos) + 1}" #pone id

        #crea el objeto evento
        try:
            nuevo_evento = Evento(
                IdEvento=nuevo_id,
                nombre=nombre,
                fecha=fecha,
                ubicacion=ubicacion,
                organizador=organizador,
                numMesas=numMesas
            )
            
            #guarda el evento en edicion acutal
            self.evento_en_edicion_actual = nuevo_evento
            
        except Exception as e:
            QMessageBox.critical(self, "Error")
            return#sale

        # 6. Actualiza las listas de la Pág 6 y muéstrala
        self.actualizar_listas_participantes()
        self.setCurrentIndex(6) # Ir a la página 6

    def anadir_participante_al_evento(self):

        #comprueba que tega el evento en edicion actual
        if self.evento_en_edicion_actual is None:
            QMessageBox.critical(self, "Error")
            return#sale

        #coge el nombre
        nombre_participante = self.pagina_participantes.ui.Input_ParticipantName.text()

        #comprobacion de que no este vacio
        if not nombre_participante:
            QMessageBox.warning(self, "Oye", "Escribe el nombre del participante.")
            return#si no esta sale
            
        #le crea el id al participante
        evento_id = self.evento_en_edicion_actual.IdEvento
        num_part = len(self.evento_en_edicion_actual.participantes)
        participante_id = f"{evento_id}_p_{num_part + 1}"

        #crea el participante
        nuevo_participante = Participante(participante_id, nombre_participante)

        #añade el participante
        self.evento_en_edicion_actual.anadirparticipante(nuevo_participante)
        
        #limpia los txtdfields
        self.pagina_participantes.ui.Input_ParticipantName.setText("")
        #refresca
        self.actualizar_listas_participantes()

    def actualizar_listas_participantes(self):

        #guardo las tablas todas
        lista_invitados = self.pagina_participantes.ui.List_AllGuests
        lista_pref = self.pagina_participantes.ui.List_Preference
        lista_no = self.pagina_participantes.ui.List_Avoid
        
        #vcia todas las tablas
        lista_invitados.clear()
        lista_pref.clear()
        lista_no.clear()

        #si hay un evento en edicion rellena la de invitados
        if self.evento_en_edicion_actual:

            for participante in self.evento_en_edicion_actual.participantes:
                lista_invitados.addItem(participante.nombre)
        
    def guardar_evento_y_participantes(self):

        #comprueba que haya aux
        if self.evento_en_edicion_actual is None:
            QMessageBox.critical(self, "Error", "No hay evento que guardar.")
            return

        #añade el evento aux a la lista
        self.lista_eventos.append(self.evento_en_edicion_actual)

        #Guarda en el json
        self.gestor_datos.guardarEventos(self.lista_eventos)

        #vacia el aux
        self.evento_en_edicion_actual = None
        
        #vacia todos los txt
        self.pagina_crear.ui.Input_EventName.setText("")
        self.pagina_crear.ui.Input_EventDate.setText("")
        self.pagina_crear.ui.Input_EventLocation.setText("")
        self.pagina_crear.ui.Input_EventOrganizer.setText("")
        self.pagina_crear.ui.Input_NumTables.setValue(1)

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

    def actualizar_tabla_borrar(self,ruta):
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

    def Crear_SubirCSV(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Selecciona un archivo CSV", "", "Archivos CSV (*.csv)")
        if archivo:
            try:
                df = pd.read_csv(archivo)
                print("Archivo cargado con éxito:")
                print(df.head())
                
                # Ejemplo: agregar participantes desde CSV
                if self.evento_en_edicion_actual:
                    for nombre in df.iloc[:,0]:  # asume que la primera columna tiene los nombres
                        participante_id = f"{self.evento_en_edicion_actual.IdEvento}_p_{len(self.evento_en_edicion_actual.participantes) + 1}"
                        nuevo_participante = Participante(participante_id, nombre)
                        self.evento_en_edicion_actual.anadirparticipante(nuevo_participante)
                    
                    self.actualizar_listas_participantes()  # refresca lista en interfaz
                    QMessageBox.information(self, "Éxito", "Participantes importados desde CSV")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo leer el CSV:\n{str(e)}")
        else:
            QMessageBox.warning(self, "Cancelado", "No se seleccionó ningún archivo")

    def seleccionar_csv(self,ruta):
        ruta, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo CSV", "", "CSV Files (*.csv)")
        self.actualizar_tabla_crud(ruta)
        if ruta:
            self.cargar_csv(ruta)
    
    def cargar_csv(self, ruta):
        df = pd.read_csv(ruta)
        self.tabla.setRowCount(len(df))
        self.tabla.setColumnCount(len(df.columns))
        self.tabla.setHorizontalHeaderLabels(df.columns)

        for i in range(len(df)):
            for j in range(len(df.columns)):
                self.tabla.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))

    def mostrar_pagina_auto(self):
        self.setCurrentIndex(7)

    def mostrar_pagina_excepciones(self):
        self.setCurrentIndex(8)

    def algoritmo_asignar_mesas(self, participantes, mesas):
        # Barajar la lista de participantes
        random.shuffle(participantes)
        excepciones = []

        # Comprobar que hay mesas
        if not mesas:
            print("Error: No hay mesas para asignar.")
            return participantes  # Todos son excepciones si no hay mesas

        # Coger la capacidad de la primera mesa (asumimos que todas son iguales)
        capacidad_por_mesa = mesas[0].capacidad
        if capacidad_por_mesa <= 0:
            print("Error: La capacidad de la mesa es 0 o negativa.")
            return participantes  # Todos son excepciones

        # Asignar participantes uno por uno (tu lógica)
        for i, participante in enumerate(participantes):
            indice_mesa = i // capacidad_por_mesa

            if indice_mesa < len(mesas):
                mesas[indice_mesa].anadirParticipante(participante)
                participante.asignar_mesa(mesas[indice_mesa].id_mesa)
            else:
                excepciones.append(participante)

        return excepciones


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

    def guardar_evento_actualizado(self):
        if self.evento_en_edicion_actual is None:
            QMessageBox.critical(self, "Error", "No hay ningún evento seleccionado para editar.")
            return

        nuevo_nombre = self.pagina_actualizar.ui.Input_EventName.text()
        nueva_fecha = self.pagina_actualizar.ui.Input_EventDate.text()
        nueva_ubicacion = self.pagina_actualizar.ui.Input_EventLocation.text()
        nuevo_organizador = self.pagina_actualizar.ui.Input_EventOrganizer.text()
        nuevo_numMesas = self.pagina_actualizar.ui.Input_NumTables.value()

        if not nuevo_nombre or not nueva_fecha:
            QMessageBox.warning(self, "Oye", "Pon el nombre y la fecha")
            return

        self.evento_en_edicion_actual.nombre = nuevo_nombre
        self.evento_en_edicion_actual.fecha = nueva_fecha
        self.evento_en_edicion_actual.ubicacion = nueva_ubicacion
        self.evento_en_edicion_actual.organizador = nuevo_organizador

        if self.evento_en_edicion_actual.numMesas != nuevo_numMesas:
            self.evento_en_edicion_actual.numMesas = nuevo_numMesas
            self.evento_en_edicion_actual.mesas = []
            capacidad_por_mesa = 10

            for i in range(nuevo_numMesas):
                id_mesa = f"{self.evento_en_edicion_actual.IdEvento}_mesa_{i+1}"
                nueva_mesa = Mesa(id_mesa=id_mesa, numero=i + 1, capacidad=capacidad_por_mesa)
                self.evento_en_edicion_actual.mesas.append(nueva_mesa)

            QMessageBox.warning(
                self,
                "Oye",
                "Se actualizó el número de mesas. Tendrás que asignar los participantes de nuevo."
            )

        self.gestor_datos.guardarEventos(self.lista_eventos)
        self.evento_en_edicion_actual = None
        self.mostrar_pagina_crud()


    def borrar_evento_seleccionado(self):
        tabla_borrar = self.pagina_borrar.ui.EventList_Table_Delete
        fila_seleccionada = tabla_borrar.currentRow()

        if fila_seleccionada == -1:
            QMessageBox.warning(self, "Oye", "No has seleccionado ningún evento.")
            return

        try:
            evento_a_borrar = self.lista_eventos[fila_seleccionada]
            nombre_evento = evento_a_borrar.nombre
        except IndexError:
            QMessageBox.critical(self, "Error", "No se ha podido borrar el evento.")
            return

        confirmacion = QMessageBox.question(
            self,
            "Confirmar borrado",
            f"¿Estás seguro de que quieres borrar el evento '{nombre_evento}'?\n\nEsta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirmacion == QMessageBox.Yes:
            self.lista_eventos.pop(fila_seleccionada)
            self.gestor_datos.guardarEventos(self.lista_eventos)
            self.actualizar_tabla_borrar()
            self.mostrar_pagina_crud()
        else:
            return


    def cargar_y_actualizar_eventos(self):
        self.lista_eventos = self.gestor_datos.cargarEventos()
        self.actualizar_tabla_crud()


    def cargar_y_actualizar_eventos_borrar(self):
        self.lista_eventos = self.gestor_datos.cargarEventos()
        self.actualizar_tabla_borrar()


    def guardar_nuevo_evento(self):
        nombre = self.pagina_crear.ui.Input_EventName.text()
        fecha = self.pagina_crear.ui.Input_EventDate.text()
        ubicacion = self.pagina_crear.ui.Input_EventLocation.text()
        organizador = self.pagina_crear.ui.Input_EventOrganizer.text()
        numMesas = self.pagina_crear.ui.Input_NumTables.value()

        if not nombre or not fecha:
            QMessageBox.warning(self, "Oye", "Pon el nombre y la fecha")
            return

        nuevo_id = f"evento_{len(self.lista_eventos) + 1}"

        try:
            nuevo_evento = Evento(
                IdEvento=nuevo_id,
                nombre=nombre,
                fecha=fecha,
                ubicacion=ubicacion,
                organizador=organizador,
                numMesas=numMesas
            )
        except Exception:
            QMessageBox.critical(self, "Error", "No se ha podido crear el evento.")
            return

        self.lista_eventos.append(nuevo_evento)
        self.gestor_datos.guardarEventos(self.lista_eventos)

        self.pagina_crear.ui.Input_EventName.setText("")
        self.pagina_crear.ui.Input_EventDate.setText("")
        self.pagina_crear.ui.Input_EventLocation.setText("")
        self.pagina_crear.ui.Input_EventOrganizer.setText("")
        self.pagina_crear.ui.Input_NumTables.setValue(1)

        self.mostrar_pagina_crud()


    def actualizar_tabla_crud(self):
        tabla = self.pagina_crud.ui.EventList_Table
        tabla.blockSignals(True)
        tabla.setRowCount(0)

        for evento in self.lista_eventos:
            row_position = tabla.rowCount()
            tabla.insertRow(row_position)
            tabla.setItem(row_position, 0, QTableWidgetItem(evento.nombre))
            tabla.setItem(row_position, 1, QTableWidgetItem(evento.fecha))
            tabla.setItem(row_position, 2, QTableWidgetItem(evento.ubicacion))
            tabla.setItem(row_position, 3, QTableWidgetItem(evento.organizador))

        tabla.blockSignals(False)


    def actualizar_tabla_borrar(self):
        tabla = self.pagina_borrar.ui.EventList_Table_Delete
        tabla.blockSignals(True)
        tabla.setRowCount(0)

        for evento in self.lista_eventos:
            row_position = tabla.rowCount()
            tabla.insertRow(row_position)
            tabla.setItem(row_position, 0, QTableWidgetItem(evento.nombre))
            tabla.setItem(row_position, 1, QTableWidgetItem(evento.fecha))
            tabla.setItem(row_position, 2, QTableWidgetItem(evento.ubicacion))
            tabla.setItem(row_position, 3, QTableWidgetItem(evento.organizador))

        tabla.blockSignals(False)
    
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
                    nombre_participante = row.get('Nombre')
                    
                    if not nombre_participante: # Ignorar filas sin nombre
                        continue
                        
                    # Crear el participante (misma lógica que anadir_participante_al_evento)
                    evento_id = self.evento_en_edicion_actual.IdEvento
                    num_part = len(self.evento_en_edicion_actual.participantes)
                    participante_id = f"{evento_id}_p_{num_part + 1}"
                    
                    nuevo_participante = Participante(participante_id, nombre_participante)

                    # Añadir preferencias
                    pref_texto = row.get('Preferencias', '') # Coge el texto o un string vacío
                    if pref_texto:
                        # Separa los nombres por ";" y quita espacios en blanco
                        lista_pref = [nombre.strip() for nombre in pref_texto.split(';')]
                        nuevo_participante.preferencias = lista_pref

                    # Añadir evitados
                    evit_texto = row.get('Evitados', '')
                    if evit_texto:
                        lista_evit = [nombre.strip() for nombre in evit_texto.split(';')]
                        nuevo_participante.evitados = lista_evit
                    
                    # Añadir el participante al evento
                    self.evento_en_edicion_actual.anadirparticipante(nuevo_participante)
                    participantes_cargados += 1

            QMessageBox.information(self, "Éxito", f"Se han cargado {participantes_cargados} participantes desde el CSV.")
            
            # (Opcional) Si quieres ir a la Pág 6 para ver la lista, descomenta esto:
            # self.editar_participantes_de_evento() 

        except Exception as e:
            QMessageBox.critical(self, "Error al leer CSV", f"No se pudo leer el archivo.\nError: {e}")

#Ejecuta
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec_())