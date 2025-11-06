import sys
# Importa las clases necesarias de PyQt5
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog

# Importa las clases de UI generadas
from controllers.ControllerCrudEvento import Ui_MainWindow
from controllers.CrearEvento1Controller import Ui_Form  # <-- 1. Importación corregida

# --- 2. Crea una clase para tu diálogo "Crear Evento" ---
# Esta clase usa la UI 'Ui_Form' dentro de un QDialog
class DialogoCrearEvento(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configura la UI (Ui_Form) en este QDialog
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
        # (Opcional) Conectar botones del diálogo
        self.ui.btnFinalizar.clicked.connect(self.accept)  # Cierra el diálogo con "Aceptar"
        self.ui.btnAtras_3.clicked.connect(self.reject)    # Cierra el diálogo con "Cancelar"


# --- 3. Tu Ventana Principal (casi sin cambios) ---
class MiVentana(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configura la UI principal (Ui_MainWindow)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # --- 4. Conecta el botón para abrir el diálogo ---
        # Ya no necesitas QStackedWidget ni la importación del módulo
        self.ui.btnCrearEvento.clicked.connect(self.abrir_dialogo_crear)

    def abrir_dialogo_crear(self):
        """
        Crea y muestra el diálogo para crear un nuevo evento.
        """
        # Crea una instancia de tu clase de diálogo
        dialogo = DialogoCrearEvento(self)  # 'self' lo hace hijo de la ventana principal
        
        # Muestra el diálogo de forma "modal"
        # (bloquea la ventana principal hasta que se cierre el diálogo)
        result = dialogo.exec_()
        
        # (Opcional) Puedes comprobar si el usuario hizo clic en "Finalizar"
        if result == QDialog.Accepted:
            print("Diálogo aceptado. Aquí iría la lógica para guardar el evento.")
            # Ejemplo:
            # nombre = dialogo.ui.txtNombre_3.text()
            # fecha = dialogo.ui.txtFecha_3.text()
            # ...hacer algo con los datos...


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MiVentana()
    ventana.show()
    sys.exit(app.exec_())