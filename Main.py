import sys
from PyQt5.QtWidgets import QApplication, QWidget, QStackedWidget, QMessageBox, QTableWidgetItem

#Importa las vistas
from controllers.CrudEvento import Ui_MainWindow
from controllers.ControllerCrearEvento1 import Ui_Form as Ui_CrearEventoForm
from controllers.ControllerAsignarMesas import Ui_Form as Ui_PaginaMesas
from controllers.EditarEvento import Ui_Form as Ui_ActualizarEventoForm
from controllers.ControllerAsignarMesasManual import Ui_Form as Ui_AsignarManual


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

        

#Ventana principal
class VentanaPrincipal(QStackedWidget):
    def __init__(self):
        super().__init__()
        
        #el json bd
        self.gestor_datos = GestorDatos("eventos.json") 
        #para guardar todos los eventoss
        self.lista_eventos = []
        
        #Las paginas
        self.pagina_crud = PaginaCrud()           #0
        self.pagina_crear = PaginaCrearEvento()     #1
        self.pagina_actualizar = PaginaActualizarEvento() #2
        self.pagina_mesas = PaginaMesas()         #3
        self.pagina_manual=Manual()             #4
        
        #añade las paginas
        self.addWidget(self.pagina_crud)           #0
        self.addWidget(self.pagina_crear)         #1
        self.addWidget(self.pagina_actualizar)    #2
        self.addWidget(self.pagina_mesas)          #3
        self.addWidget(self.pagina_manual)          #4

        #Conecta los botones
        #botones del crud 0
        self.pagina_crud.ui.CreateEvent_Btn.clicked.connect(self.mostrar_pagina_crear)
        self.pagina_crud.ui.UpdateEvent_Btn.clicked.connect(self.mostrar_pagina_actualizar)
        self.pagina_crud.ui.AssignTables_Btn.clicked.connect(self.mostrar_pagina_mesas)
        self.pagina_mesas.ui.ManualAssign_Btn.clicked.connect(self.mostrar_pagina_manual)
        #falta el boton de borrar
        # self.pagina_crud.ui.DeleteEvent_Btn.clicked.connect(self.mostrar_pagina_borrar) 

        #mas botones
        #boton atras 1
        self.pagina_crear.ui.BackButton_CreateEvent.clicked.connect(self.mostrar_pagina_crud)
        self.pagina_manual.ui.BackButton_ManualAssign.clicked.connect(self.mostrar_pagina_mesas)

        #boton finalizar
        self.pagina_crear.ui.FinishCreateEvent_Btn.clicked.connect(self.guardar_nuevo_evento)
        
        #atras de actualizar evento 2
        self.pagina_actualizar.ui.BackButton_UpdateEvent.clicked.connect(self.mostrar_pagina_crud)
        
        #atras de asignar mesas 3
        self.pagina_mesas.ui.BackButton_AssignMenu.clicked.connect(self.mostrar_pagina_crud)
        
        #falta poner el resto de botones de atras

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
        #falta cargr los campos conlos daosd del evento selecionado
        self.setCurrentIndex(2)

    def mostrar_pagina_mesas(self):
        self.setCurrentIndex(3)

    def mostrar_pagina_manual(self):
        self.setCurrentIndex(4)
    



    #mas metodos varios

    def cargar_y_actualizar_eventos(self):
        self.lista_eventos = self.gestor_datos.cargarEventos()
        self.actualizar_tabla_crud()

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
            QMessageBox.warning(
                self,  
                "Oye", 
                "Pon el nombre y la fecha"
            )       
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


#Ejecuta
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec_())