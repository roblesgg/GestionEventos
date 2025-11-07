# --- Importaciones ---
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QStackedWidget, QMessageBox
from controllers.CrudEvento import Ui_MainWindow
from controllers.ControllerCrearEvento1 import Ui_Form as Ui_CrearEventoForm
# ======================================================================
# ### PASO 1: IMPORTA TU NUEVA VENTANA ###
# ======================================================================
# CORREGIDO: Asumimos que "Actualizar Evento" es tu archivo EditarEvento.py
# (ya que ActualizarEventoController.py no existe)
from controllers.EditarEvento import Ui_Form as Ui_ActualizarEventoForm
# ======================================================================


# --- 2. Clases de "Página" (Widgets) ---
# Creamos una clase por cada ventana/página que queramos mostrar.
# Estas clases heredan de QWidget y "cargan" el diseño de la UI.

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
        
# ======================================================================
# ### PASO 2: CREA LA CLASE PARA TU NUEVA PÁGINA ###
# ======================================================================
# Copia y pega la clase anterior y cambia el nombre de la UI
# que debe cargar.
class PaginaActualizarEvento(QWidget):
    def __init__(self):
        super().__init__()
        # 2.1 - Carga el diseño de 'ActualizarEvento'
        self.ui = Ui_ActualizarEventoForm()
        # 2.2 - "Dibuja" la UI en este widget
        self.ui.setupUi(self)
# ======================================================================


# --- 3. Controlador Principal (El "Mazo de Cartas") ---
# Esta es la clase principal que contiene todas las demás páginas.
# Hereda de QStackedWidget.
class VentanaPrincipal(QStackedWidget):
    def __init__(self):
        super().__init__()
        
        # --- 4. Crea las Instancias de las Páginas ---
        # Creamos un objeto (una "carta") por cada clase de página.
        self.pagina_crud = PaginaCrud()#0
        self.pagina_crear = PaginaCrearEvento()#1
        
        # ======================================================================
        # ### PASO 3: CREA LA INSTANCIA DE TU NUEVA PÁGINA ###
        # ======================================================================
        self.pagina_actualizar = PaginaActualizarEvento()#2
        # ======================================================================

        # --- 5. Añade las Páginas al "Mazo" ---
        # El orden importa. La primera que añades (Índice 0) es la que se muestra
        # al arrancar la aplicación.
        self.addWidget(self.pagina_crud)           # Índice 0
        self.addWidget(self.pagina_crear)         # Índice 1
        
        # ======================================================================
        # ### PASO 4: AÑADE TU NUEVA PÁGINA AL MAZO ###
        # ======================================================================
        self.addWidget(self.pagina_actualizar)    # Índice 2
        # ======================================================================

        # --- 6. Conecta los Botones (Señales) ---
        # Aquí conectamos los clics de los botones a las funciones
        # que cambian de página.
        
        # --- Botones de la Página CRUD (Índice 0) ---
        
        # Conecta: PaginaCrud -> CreateEvent_Btn -> mostrar_pagina_crear
        # NOTA: Usamos el ID nuevo 'CreateEvent_Btn'
        self.pagina_crud.ui.CreateEvent_Btn.clicked.connect(self.mostrar_pagina_crear)
        
        # ======================================================================
        # ### PASO 5: CONECTA EL BOTÓN DE TU NUEVA PÁGINA ###
        # ======================================================================
        # Conecta: PaginaCrud -> UpdateEvent_Btn -> mostrar_pagina_actualizar
        # NOTA: Usamos el ID nuevo 'UpdateEvent_Btn'
        self.pagina_crud.ui.UpdateEvent_Btn.clicked.connect(self.mostrar_pagina_actualizar)
        # ======================================================================

        # --- Botones de la Página Crear Evento (Índice 1) ---
        
        # Conecta: PaginaCrearEvento -> BackButton_CreateEvent -> mostrar_pagina_crud
        # NOTA: Usamos el ID nuevo 'BackButton_CreateEvent'
        self.pagina_crear.ui.BackButton_CreateEvent.clicked.connect(self.mostrar_pagina_crud)
        
        # ======================================================================
        # ### PASO 5 (bis): CONECTA EL BOTÓN DE "ATRÁS" DE TU NUEVA PÁGINA ###
        # ======================================================================
        # Conecta: PaginaActualizarEvento -> BackButton_UpdateEvent -> mostrar_pagina_crud
        # NOTA: El ID 'BackButton_UpdateEvent' debe existir en tu 'EditarEvento.ui'
        # Si usaste 'ActualizarEvento.ui' que te di, este ID es correcto.
        self.pagina_actualizar.ui.BackButton_UpdateEvent.clicked.connect(self.mostrar_pagina_crud)
        # ======================================================================

        # Ajusta el tamaño de la ventana principal
        self.resize(904, 617) # El tamaño de tu UI principal

    # --- 7. Funciones para Cambiar de Página ---
    # Estas funciones son las que se llaman al hacer clic.
    
    # Muestra la página CRUD (Índice 0)
    def mostrar_pagina_crud(self):
        self.setCurrentIndex(0)
        
    # Muestra la página Crear Evento (Índice 1)
    def mostrar_pagina_crear(self):
        self.setCurrentIndex(1) 

    # ======================================================================
    # ### PASO 6: CREA LA FUNCIÓN PARA MOSTRAR TU NUEVA PÁGINA ###
    # ======================================================================
    # Muestra la página Actualizar Evento (Índice 2)
    def mostrar_pagina_actualizar(self):
        
        # --- LÓGICA OPCIONAL ---
        # Aquí es donde deberías cargar los datos del evento seleccionado
        # en la tabla ANTES de mostrar la página.
        #
        # 1. Mira qué fila está seleccionada en la tabla del CRUD
        #    fila_seleccionada = self.pagina_crud.ui.EventList_Table.currentRow()
        # 2. Si no hay nada seleccionado (fila_seleccionada == -1), muestra un error o no hagas nada.
        # 3. Coge los datos de esa fila.
        # 4. Rellena los campos de la página_actualizar:
        #    self.pagina_actualizar.ui.Input_EventName.setText("Nombre de la fila")
        #    self.pagina_actualizar.ui.Input_EventDate.setText("Fecha de la fila")
        #    ...etc.
        
        # Solo después de rellenar los datos, cambia de página
        self.setCurrentIndex(2)
    # ======================================================================



    #Metodo al pulsar boton finalizar en crear evento para guardar toda la info
def guardar_nuevo_evento(self):

    #Guarda los datos de los txt
    nombre = self.pagina_crear.ui.Input_EventName.text()
    fecha = self.pagina_crear.ui.Input_EventDate.text()
    ubicacion = self.pagina_crear.ui.Input_EventLocation.text()
    organizador = self.pagina_crear.ui.Input_EventOrganizer.text()

    #Comprueba que no falte nombre ni fecha
    if not nombre or not fecha:
        QMessageBox.warning(
            self,  # El 'padre' (la ventana actual)
            "Datos Incompletos",  #Titulo d la ventana
            "El nombre y la fecha son campos obligatorios." # Mensaje
        )       
        return#Se sale del metodo
    # 3. Crea el "Molde" (un objeto Evento, o un simple diccionario)
    nuevo_evento = {
        "id": "evento_" + str(len(self.lista_eventos)), # Un ID simple por ahora
        "nombre": nombre,
        "fecha": fecha,
        "ubicacion": ubicacion,
        "organizador": organizador,
        "participantes": [] # Lista vacía al crear
    }

    self.lista_eventos.append(nuevo_evento)

    # (Asumimos que 'self.gestor_datos' es nuestro objeto GestorDatos.py)
    # self.gestor_datos.guardar_eventos(self.lista_eventos)

    print(f"Evento guardado: {nuevo_evento['nombre']}")

    # 5. (Opcional) Limpia los campos de texto
    self.pagina_crear.ui.Input_EventName.setText("")
    # ...etc.

    # 6. Vuelve al CRUD
    self.mostrar_pagina_crud()

    # 7. Actualiza la tabla del CRUD (¡Importante!)
    self.actualizar_tabla_crud()

def actualizar_tabla_crud(self):
    # ... (Aquí va el código para leer 'self.lista_eventos' 
    # y rellenar 'self.pagina_crud.ui.EventList_Table')
    pass


# --- 8. Ejecución de la aplicación ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Crea nuestra ventana principal (el 'QStackedWidget')
    ventana = VentanaPrincipal()
    
    # ¡Muestra la ventana!
    ventana.show()
    
    # Inicia la aplicación
    sys.exit(app.exec_())