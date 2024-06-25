import sys
from PyQt5.QtWidgets import QApplication
from ventana_libros import VentanaLibros

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VentanaLibros()
    window.show()
    sys.exit(app.exec_())
