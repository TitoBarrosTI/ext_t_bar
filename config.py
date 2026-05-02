# config.py
import json
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "config.json"

DEFAULT_CONFIG = {"groups": []}

def load_config() -> dict:
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config: dict) -> None:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def get_groups() -> list:
    return load_config().get("groups", [])

def add_group(name: str) -> None:
    config = load_config()
    config["groups"].append({"name": name, "shortcuts": []})
    save_config(config)

def remove_group(index: int) -> None:
    config = load_config()
    config["groups"].pop(index)
    save_config(config)

def add_shortcut(group_index: int, name: str, path: str) -> None:
    config = load_config()
    config["groups"][group_index]["shortcuts"].append({"name": name, "path": path})
    save_config(config)

def remove_shortcut(group_index: int, shortcut_index: int) -> None:
    config = load_config()
    config["groups"][group_index]["shortcuts"].pop(shortcut_index)
    save_config(config)