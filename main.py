import logging

from setup import run_setup
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
    run_setup()
    
    # try connect first
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

    # daemon is not running - go up once and wait
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

if __name__ == "__main__":
    main()