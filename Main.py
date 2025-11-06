import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog

from ControllerCrudEvento import Ui_MainWindow 

from CrearEvento1Controller import Ui_DialogoCrearEvento


class MiVentana(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow() 
        self.ui.setupUi(self)
        self.ui.btnCrearEvento.clicked.connect(self.abrir_crearEvento1)
        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MiVentana()
    ventana.show()
    sys.exit(app.exec_())