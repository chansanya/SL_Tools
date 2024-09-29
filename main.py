
from QTBackupApp import QTBackupApp
from PyQt5.QtWidgets import QApplication
from config.config import   check_file


is_tk_ui = False

if __name__ == "__main__":
    check_file()
    app = QApplication([])
    window = QTBackupApp()
    window.show()
    app.exec_()
