import logging
logging.basicConfig(filename="daemon.log", level=logging.DEBUG)

# daemon.py
import sys
import socket
import threading
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, Signal, QObject

from winapi import set_app_user_model_id, is_already_running
from popup import PopupLauncher

HOST = "127.0.0.1"
PORT = 59871
MUTEX_NAME = "ExtTBar_Daemon"

class SignalBridge(QObject):
    show_popup = Signal()

class Daemon:
    def __init__(self, app: QApplication):
        self._app = app
        self._bridge = SignalBridge()
        self._bridge.show_popup.connect(self._show_popup)
        self._popup = None

    def _show_popup(self):
        logging.debug("_show_popup chamado")
        try:
            if self._popup and self._popup.isVisible():
                self._popup.close()
                return
            self._popup = PopupLauncher()
            logging.debug("popup criado")
            self._popup.show()
            self._popup.raise_()
            self._popup.activateWindow()
            logging.debug("popup mostrado")
        except Exception as e:
            logging.exception(f"erro ao mostrar popup: {e}")

    def start_socket(self):
        def listen():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((HOST, PORT))
                s.listen()
                logging.debug("daemon escutando")
                while True:
                    conn, _ = s.accept()
                    with conn:
                        conn.recv(16)
                    logging.debug("sinal recebido, emitindo show_popup")
                    self._bridge.show_popup.emit()

        t = threading.Thread(target=listen, daemon=True)
        t.start()

if __name__ == "__main__":
    if is_already_running(MUTEX_NAME):
        sys.exit(0)

    set_app_user_model_id("TitoBarrosTI.ExtTBar.Daemon")

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # não encerra ao fechar popup

    daemon = Daemon(app)
    daemon.start_socket()

    sys.exit(app.exec())