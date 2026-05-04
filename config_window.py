# config_window.py
from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                                QPushButton, QListWidget, QListWidgetItem,
                                QFileDialog, QLineEdit, QLabel,
                                QApplication, QSplitter)
from PySide6.QtCore import Qt

from config import get_groups, add_group, remove_group, add_shortcut, remove_shortcut

WINDOW_BG  = "#2b2b2b"
PANEL_BG   = "#222222"
BTN_BLUE   = "#4f8ef7"
BTN_RED    = "#e06c75"
BTN_GRAY   = "#555555"
INPUT_BG   = "#3c3c3c"
TEXT_COLOR = "#cccccc"
WHITE      = "#ffffff"

class ConfigWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ExtTaskBar — Configurações")
        self.setMinimumSize(600, 400)
        self.setStyleSheet(f"background-color: {WINDOW_BG}; color: {TEXT_COLOR};")
        self._selected_group = 0
        self._build_ui()
        self._load_groups()

    def _build_ui(self):
        root = QHBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_left_panel())
        root.addWidget(self._build_right_panel())

        self.setLayout(root)

    # ── painel esquerdo: grupos ──────────────────────────────────────

    def _build_left_panel(self) -> QWidget:
        panel = QWidget()
        panel.setFixedWidth(180)
        panel.setStyleSheet(f"background-color: {PANEL_BG};")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        lbl = QLabel("Grupos")
        lbl.setStyleSheet("font-size: 11px; color: #888888;")
        layout.addWidget(lbl)

        self._group_list = QListWidget()
        self._group_list.setStyleSheet(self._list_style())
        self._group_list.currentRowChanged.connect(self._on_group_changed)
        layout.addWidget(self._group_list)

        self._input_group = QLineEdit()
        self._input_group.setPlaceholderText("Nome do grupo")
        self._input_group.setStyleSheet(self._input_style())
        layout.addWidget(self._input_group)

        btn_add = QPushButton("+ Adicionar grupo")
        btn_add.clicked.connect(self._add_group)
        btn_add.setStyleSheet(self._btn_style(BTN_BLUE))
        layout.addWidget(btn_add)

        btn_rem = QPushButton("Remover grupo")
        btn_rem.clicked.connect(self._remove_group)
        btn_rem.setStyleSheet(self._btn_style(BTN_RED))
        layout.addWidget(btn_rem)

        return panel

    # ── painel direito: atalhos do grupo ────────────────────────────

    def _build_right_panel(self) -> QWidget:
        panel = QWidget()
        panel.setStyleSheet(f"background-color: {WINDOW_BG};")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        lbl = QLabel("Atalhos")
        lbl.setStyleSheet("font-size: 11px; color: #888888;")
        layout.addWidget(lbl)

        self._shortcut_list = QListWidget()
        self._shortcut_list.setStyleSheet(self._list_style())
        layout.addWidget(self._shortcut_list)

        btn_rem = QPushButton("Remover selecionado")
        btn_rem.clicked.connect(self._remove_shortcut)
        btn_rem.setStyleSheet(self._btn_style(BTN_RED))
        layout.addWidget(btn_rem)

        lbl2 = QLabel("Adicionar atalho")
        lbl2.setStyleSheet("font-size: 11px; color: #888888; margin-top: 6px;")
        layout.addWidget(lbl2)

        self._input_name = QLineEdit()
        self._input_name.setPlaceholderText("Nome")
        self._input_name.setStyleSheet(self._input_style())
        layout.addWidget(self._input_name)

        row = QHBoxLayout()
        self._input_path = QLineEdit()
        self._input_path.setPlaceholderText("Caminho do executável")
        self._input_path.setStyleSheet(self._input_style())
        row.addWidget(self._input_path)

        btn_browse = QPushButton("...")
        btn_browse.setFixedWidth(36)
        btn_browse.clicked.connect(self._browse)
        btn_browse.setStyleSheet(self._btn_style(BTN_GRAY))
        row.addWidget(btn_browse)
        layout.addLayout(row)

        btn_add = QPushButton("Adicionar atalho")
        btn_add.clicked.connect(self._add_shortcut)
        btn_add.setStyleSheet(self._btn_style(BTN_BLUE))
        layout.addWidget(btn_add)

        return panel

    # ── dados ────────────────────────────────────────────────────────

    def _load_groups(self):
        self._group_list.clear()
        for g in get_groups():
            self._group_list.addItem(g["name"])
        if self._group_list.count():
            self._group_list.setCurrentRow(0)

    def _load_shortcuts(self, group_index: int):
        self._shortcut_list.clear()
        groups = get_groups()
        if group_index < 0 or group_index >= len(groups):
            return
        for s in groups[group_index].get("shortcuts", []):
            self._shortcut_list.addItem(f"{s['name']}  —  {s['path']}")

    def _on_group_changed(self, row: int):
        self._selected_group = row
        self._load_shortcuts(row)

    def _add_group(self):
        name = self._input_group.text().strip()
        if not name:
            return
        add_group(name)
        self._input_group.clear()
        self._load_groups()

    def _remove_group(self):
        row = self._group_list.currentRow()
        if row < 0:
            return
        remove_group(row)
        self._selected_group = 0
        self._load_groups()

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar executável", "", "Executáveis (*.exe)"
        )
        if path:
            self._input_path.setText(path)
            if not self._input_name.text().strip():
                name = Path(path).stem
                self._input_name.setText(name)

    def _add_shortcut(self):
        name = self._input_name.text().strip()
        path = self._input_path.text().strip()
        if not name or not path:
            return
        add_shortcut(self._selected_group, name, path)
        self._input_name.clear()
        self._input_path.clear()
        self._load_shortcuts(self._selected_group)

    def _remove_shortcut(self):
        row = self._shortcut_list.currentRow()
        if row < 0:
            return
        remove_shortcut(self._selected_group, row)
        self._load_shortcuts(self._selected_group)

    # ── estilos ──────────────────────────────────────────────────────

    def _list_style(self) -> str:
        return f"""
            QListWidget {{
                background-color: {INPUT_BG};
                border: none;
                border-radius: 6px;
                color: {WHITE};
                font-size: 12px;
            }}
            QListWidget::item {{ padding: 5px; }}
            QListWidget::item:selected {{ background-color: {BTN_BLUE}; }}
        """

    def _btn_style(self, bg: str) -> str:
        return f"""
            QPushButton {{
                background-color: {bg};
                color: {WHITE};
                border: none;
                border-radius: 6px;
                padding: 6px;
                font-size: 12px;
            }}
            QPushButton:hover {{ background-color: {bg}dd; }}
        """

    def _input_style(self) -> str:
        return f"""
            QLineEdit {{
                background-color: {INPUT_BG};
                color: {WHITE};
                border: none;
                border-radius: 6px;
                padding: 6px;
                font-size: 12px;
            }}
        """

    # def closeEvent(self, event):
    #     QApplication.instance().quit()
    #     super().closeEvent(event)

    def closeEvent(self, event):
        event.accept()