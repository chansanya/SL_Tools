
from QTBackupApp import QTBackupApp
from PyQt5.QtWidgets import QApplication


is_tk_ui = False

if __name__ == "__main__":
    app = QApplication([])
    window = QTBackupApp()
    window.show()
    app.exec_()
