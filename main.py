# main.py
import sys
from PySide6.QtWidgets import QApplication
from popup import PopupLauncher
from winapi import is_already_running

MUTEX_NAME = "TaskbarLauncher_SingleInstance"

if is_already_running(MUTEX_NAME):
    sys.exit(0)

app = QApplication(sys.argv)
window = PopupLauncher()
window.show()
window.raise_()
window.activateWindow()
sys.exit(app.exec())