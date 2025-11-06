import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QStackedWidget, QTableWidget, QTableWidgetItem,
    QLineEdit, QFormLayout
)
from PyQt5.QtCore import Qt


class PaginaInicio(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        etiqueta = QLabel("Bienvenido a la página de Inicio")
        etiqueta.setAlignment(Qt.AlignCenter)
        boton = QPushButton("Presióname")
        boton.setStyleSheet("background-color: #3498db; color: white;")

        layout.addWidget(etiqueta)
        layout.addWidget(boton)
        layout.addStretch()

        self.setLayout(layout)


class PaginaPerfil(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout()

        layout.addRow("Nombre:", QLineEdit())
        layout.addRow("Correo:", QLineEdit())
        layout.addRow("Teléfono:", QLineEdit())

        boton_guardar = QPushButton("Guardar cambios")
        layout.addRow(boton_guardar)

        self.setLayout(layout)


class PaginaConfig(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        tabla = QTableWidget(3, 2)
        tabla.setHorizontalHeaderLabels(["Configuración", "Valor"])
        tabla.setItem(0, 0, QTableWidgetItem("Modo oscuro"))
        tabla.setItem(0, 1, QTableWidgetItem("Activado"))
        tabla.setItem(1, 0, QTableWidgetItem("Idioma"))
        tabla.setItem(1, 1, QTableWidgetItem("Español"))
        tabla.setItem(2, 0, QTableWidgetItem("Notificaciones"))
        tabla.setItem(2, 1, QTableWidgetItem("Sí"))

        layout.addWidget(tabla)
        self.setLayout(layout)


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ejemplo de Barra de Navegación - PyQt5")
        self.setGeometry(200, 200, 900, 500)

        contenedor_principal = QWidget()
        layout_principal = QHBoxLayout(contenedor_principal)

        # --- Barra lateral ---
        barra_lateral = QVBoxLayout()
        barra_lateral.setContentsMargins(10, 10, 10, 10)
        barra_lateral.setSpacing(10)

        btn_inicio = QPushButton("Inicio")
        btn_perfil = QPushButton("Perfil")
        btn_config = QPushButton("Configuración")

        for btn in [btn_inicio, btn_perfil, btn_config]:
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2c3e50;
                    color: white;
                    border-radius: 8px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #34495e;
                }
            """)

        barra_lateral.addWidget(btn_inicio)
        barra_lateral.addWidget(btn_perfil)
        barra_lateral.addWidget(btn_config)
        barra_lateral.addStretch()

        # --- Contenido principal ---
        self.paginas = QStackedWidget()
        self.paginas.addWidget(PaginaInicio())#0
        self.paginas.addWidget(PaginaPerfil())#1
        self.paginas.addWidget(PaginaConfig())#2

        # --- Conectar botones ---
        btn_inicio.clicked.connect(lambda: self.paginas.setCurrentIndex(0))
        btn_perfil.clicked.connect(lambda: self.paginas.setCurrentIndex(1))
        btn_config.clicked.connect(lambda: self.paginas.setCurrentIndex(2))

        # --- Layout principal ---
        layout_principal.addLayout(barra_lateral, 1)
        layout_principal.addWidget(self.paginas, 4)

        self.setCentralWidget(contenedor_principal)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec_())
