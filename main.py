import sys
from PyQt5.QtWidgets import QApplication
from solar_system_app import SolarSystemApp

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SolarSystemApp()
    ex.show()
    sys.exit(app.exec_())
