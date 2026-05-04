# # main.py
# import sys
# from PySide6.QtWidgets import QApplication
# from popup import PopupLauncher
# from winapi import is_already_running, set_app_user_model_id

# MUTEX_NAME = "TaskbarLauncher_SingleInstance"

# if is_already_running(MUTEX_NAME):
#     sys.exit(0)

# set_app_user_model_id("TitoBarrosTI.ExtTBar")

# MUTEX_NAME = "ExtTBar_SingleInstance"

# app = QApplication(sys.argv)

# from PySide6.QtWidgets import QApplication, QWidget

# window = PopupLauncher()
# window.show()
# window.raise_()
# window.activateWindow()
# sys.exit(app.exec())

# main.py
import logging
logging.basicConfig(filename="main.log", level=logging.DEBUG)

import sys
import socket
import time
import subprocess
from pathlib import Path

HOST = "127.0.0.1"
PORT = 59871

def _start_daemon():
    if getattr(sys, 'frozen', False):
        # daemon = Path(sys.executable).parent / "Ext_T_Bar_daemon.exe"
        daemon = Path(sys.executable).parent / "daemon.exe"
        subprocess.Popen(
            str(daemon),
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        )
    else:
        daemon = Path(__file__).parent / "daemon.py"
        subprocess.Popen(
            [sys.executable, str(daemon)],
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        )

def main():
    # tenta conectar primeiro
    logging.debug("main iniciando")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect((HOST, PORT))
            s.sendall(b"show")
            logging.debug("sinal enviado com sucesso")
            return
    except (ConnectionRefusedError, TimeoutError, OSError) as e:
        logging.debug(f"conexão falhou: {e}")
        # pass

    # daemon não está rodando - sobe uma vez e aguarda
    logging.debug("subindo daemon")
    _start_daemon()
    time.sleep(4)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect((HOST, PORT))
            s.sendall(b"show")
            logging.debug("sinal enviado após aguardar daemon")
    except (ConnectionRefusedError, TimeoutError, OSError) as e:
        logging.debug(f"segunda conexão falhou: {e}")
        # pass

if __name__ == "__main__":
    main()