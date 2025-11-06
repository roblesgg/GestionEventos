# --- Importaciones ---
# Estas líneas traen herramientas de Python y PyQt5 que necesitamos.
import sys  # 'sys' nos deja interactuar con el sistema (como para cerrar la app)

# 'QApplication' es la aplicación en sí. 'QWidget' es una ventana vacía.
# 'QStackedWidget' es el widget especial que nos deja apilar ventanas una encima de otra.
from PyQt5.QtWidgets import QApplication, QWidget, QStackedWidget

# --- 1. Importa las clases de tus UIs ---
# Traemos el "diseño" (los botones, tablas, etc.) que creaste en Qt Designer
# y que convertiste a archivos .py.

# 'Ui_MainWindow' es el diseño de tu página principal (el CRUD con la tabla)
from controllers.ControllerCrudEvento import Ui_MainWindow
# 'Ui_Form' es el diseño de tu página para crear un evento (el formulario)
from controllers.CrearEvento1Controller import Ui_Form

# --- 2. Creamos la "Página 1" (El CRUD) ---
# Creamos una clase para tu página principal.
# Hereda de 'QWidget' (una ventana vacía), porque el QStackedWidget SÓLO
# puede apilar QWidgets.
class PaginaCrud(QWidget): # <-- Hereda de QWidget
    def __init__(self):
        # 'super().__init__()' es una línea mágica necesaria para que la clase funcione
        super().__init__()
        
        # Creamos una "instancia" de tu diseño (la UI)
        self.ui = Ui_MainWindow()
        
        # 'setupUi(self)' "dibuja" todos los botones y tablas de 'Ui_MainWindow'
        # encima de esta ventana vacía ('self').
        self.ui.setupUi(self)

# --- 3. Creamos la "Página 2" (El Formulario) ---
# Hacemos lo mismo para la página de "Crear Evento".
# Hereda de 'QWidget' (una ventana vacía).
class PaginaCrearEvento(QWidget):
    def __init__(self):
        # Línea mágica obligatoria
        super().__init__()
        
        # Creamos una instancia de tu diseño (Ui_Form)
        self.ui = Ui_Form()
        
        # "Dibuja" el formulario (labels, cajas de texto) encima de esta ventana ('self')
        self.ui.setupUi(self)

# --- 4. Creamos el Controlador Principal (La Ventana que contiene todo) ---
# Esta clase es la más importante. Hereda de 'QStackedWidget'.
# Piensa en ella como un "mazo de cartas". Cada página (PaginaCrud, PaginaCrearEvento)
# es una carta. Esta clase se encarga de mostrar solo una carta a la vez.
class VentanaPrincipal(QStackedWidget):
    def __init__(self):
        # Línea mágica obligatoria
        super().__init__()
        
        # --- 5. Crea las "cartas" (las páginas) ---
        # Creamos un objeto (una "carta") para cada página que hemos definido arriba.
        self.pagina_crud = PaginaCrud()           # Esta es la "carta" 0
        self.pagina_crear = PaginaCrearEvento()   # Esta es la "carta" 1
        
        # ======================================================================
        # ===> ¡¡PARA AÑADIR MÁS PÁGINAS (ESCALABILIDAD)!! <===
        # 1. Crea la clase para tu nueva página (igual que 'PaginaCrearEvento').
        # 2. Crea la instancia aquí:
        #    ej: self.pagina_editar = PaginaEditarEvento()
        # ======================================================================
        
        # --- 6. Añade las "cartas" al mazo (al Stack) ---
        # El orden en que las añades es importante.
        self.addWidget(self.pagina_crud)    # Índice 0
        self.addWidget(self.pagina_crear)   # Índice 1
        
        # ======================================================================
        # ===> ¡¡PARA AÑADIR MÁS PÁGINAS (ESCALABILIDAD)!! <===
        # 3. Añade tu nueva página al mazo aquí.
        #    ej: self.addWidget(self.pagina_editar) # Esta será el Índice 2
        # ======================================================================
        
        # --- 7. Conecta los botones para cambiar de página ---
        # Aquí es donde le decimos a los botones qué hacer cuando se pulsan.
        
        # Busca el botón 'btnCrearEvento' (que está DENTRO de 'pagina_crud')
        # y, cuando se haga 'clicked', llama a la función 'self.mostrar_pagina_crear'.
        self.pagina_crud.ui.btnCrearEvento.clicked.connect(self.mostrar_pagina_crear)
        
        # Busca el botón 'btnAtras_3' (que está DENTRO de 'pagina_crear')
        # y, cuando se haga 'clicked', llama a la función 'self.mostrar_pagina_crud'.
        self.pagina_crear.ui.btnAtras_3.clicked.connect(self.mostrar_pagina_crud)
        
        # ======================================================================
        # ===> ¡¡PARA AÑADIR MÁS BOTONES (ESCALABILIDAD)!! <===
        # 4. Conecta tus nuevos botones a nuevas funciones.
        #    ej: self.pagina_crud.ui.btnActualizarEvento.clicked.connect(self.mostrar_pagina_editar)
        # ======================================================================

        # Ajusta el tamaño de la ventana principal
        self.resize(904, 617) # El tamaño de tu UI principal

    # --- Funciones para cambiar de "carta" (de página) ---
    
    # Esta función se llama cuando se pulsa 'btnCrearEvento'
    def mostrar_pagina_crear(self):
        # 'setCurrentIndex(1)' le dice al mazo: "muestra la carta número 1"
        self.setCurrentIndex(1) 
        
    # Esta función se llama cuando se pulsa 'btnAtras_3'
    def mostrar_pagina_crud(self):
        # 'setCurrentIndex(0)' le dice al mazo: "muestra la carta número 0"
        self.setCurrentIndex(0)

    # ======================================================================
    # ===> ¡¡PARA AÑADIR MÁS PÁGINAS (ESCALABILIDAD)!! <===
    # 5. Crea la función que mostrará tu nueva página.
    #    ej: def mostrar_pagina_editar(self):
    #            self.setCurrentIndex(2) # Muestra la carta número 2
    # ======================================================================


# --- 8. Ejecución de la aplicación ---
# Este 'if' es estándar en Python. Solo se ejecuta si corres este
# archivo directamente (y no si lo importas desde otro).
if __name__ == "__main__":
    
    # Crea el objeto 'QApplication'. Esto es obligatorio.
    app = QApplication(sys.argv)
    
    # Crea nuestra ventana principal (el 'QStackedWidget' que lo controla todo)
    ventana = VentanaPrincipal()
    
    # ¡Muestra la ventana!
    ventana.show()
    
    # 'sys.exit(app.exec_())' inicia la aplicación y espera a que el
    # usuario la cierre. 'sys.exit' se asegura de que se cierre limpiamente.
    sys.exit(app.exec_())