# Ext_T_Bar
# Copyright (c) 2026 Tito de Barros Junior
# Licensed under the MIT License

import winreg
from pathlib import Path

REGISTRY_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "Ext_T_Bar"

def run_setup():
    exe_path = Path(__file__).parent / "ext_t_bar.exe"
    _register(str(exe_path))

def _register(exe_path: str):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe_path)
        print(f"Registered on startup: {exe_path}")
    except Exception as e:
        print(f"Error on register startup: {e}")

def _unregister():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, APP_NAME)
        print("Removed from startup.")
    except FileNotFoundError:
        print("Entry not found, nothing to remove.")
    except Exception as e:
        print(f"Error on unregister: {e}")