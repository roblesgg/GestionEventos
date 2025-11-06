import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QStackedWidget

from controllers.ControllerCrudEvento import Ui_MainWindow 

from controllers.CrearEvento1Controller import Ui_DialogoCrearEvento

from controllers import ControllerCrudEvento

class MiVentana(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # --- Contenido Principal ---
        self.paginas = QStackedWidget()
        self.paginas.addWidget(ControllerCrudEvento())#0

        # --- Conectar botones ---
        self.ui.btnCrearEvento.clicked.connect(lambda: self.paginas.setCurrentIndex(0))
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MiVentana()
    ventana.show()
    sys.exit(app.exec_())