# config_window.py
from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                                QPushButton, QListWidget, QListWidgetItem,
                                QFileDialog, QLineEdit, QLabel,
                                QApplication, QSplitter)
from PySide6.QtCore import Qt
from config import get_groups, add_group, remove_group, add_shortcut, remove_shortcut, update_shortcut

# ── paleta Gruvbox Dark ───────────────────────────────────────────────────────
WINDOW_BG    = "#282828"   # bg0
PANEL_BG     = "#1d2021"   # bg0_hard
SURFACE      = "#3c3836"   # bg1
SURFACE_HVR  = "#504945"   # bg2
SELECTED_BG  = "#504945"   # bg2
SELECTED_HL  = "#d79921"   # yellow

BTN_PRIMARY  = "#458588"   # aqua/teal
BTN_WARN     = "#d79921"   # yellow
BTN_DANGER   = "#cc241d"   # red
BTN_NEUTRAL  = "#504945"   # bg2

BORDER       = "#504945"   # bg2
TEXT_PRIMARY = "#ebdbb2"   # fg
TEXT_MUTED   = "#928374"   # gray
TEXT_LABEL   = "#a89984"   # fg4


class ConfigWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ExtTaskBar — Configurações")
        self.setMinimumSize(640, 460)
        self.setStyleSheet(f"background-color: {WINDOW_BG}; color: {TEXT_PRIMARY};")
        self._selected_group = 0
        self._editing_shortcut: int | None = None
        self._build_ui()
        self._load_groups()

    def _build_ui(self):
        root = QHBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_left_panel())
        root.addWidget(self._build_right_panel())
        self.setLayout(root)

    # ── painel esquerdo: grupos ───────────────────────────────────────────────

    def _build_left_panel(self) -> QWidget:
        panel = QWidget()
        panel.setFixedWidth(200)
        panel.setStyleSheet(f"""
            QWidget {{
                background-color: {PANEL_BG};
                border-right: 1px solid {BORDER};
            }}
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 14, 10, 12)
        layout.setSpacing(4)

        lbl = QLabel("GRUPOS")
        lbl.setStyleSheet(f"font-size: 10px; color: {TEXT_MUTED}; letter-spacing: 1px; border: none;")
        layout.addWidget(lbl)

        self._group_list = QListWidget()
        self._group_list.setStyleSheet(self._group_list_style())
        self._group_list.currentRowChanged.connect(self._on_group_changed)
        layout.addWidget(self._group_list)

        layout.addSpacing(6)

        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER}; border: none;")
        layout.addWidget(sep)

        layout.addSpacing(6)

        self._input_group = QLineEdit()
        self._input_group.setPlaceholderText("Nome do grupo...")
        self._input_group.setStyleSheet(self._input_style())
        layout.addWidget(self._input_group)

        btn_add = QPushButton("+ Adicionar grupo")
        btn_add.clicked.connect(self._add_group)
        btn_add.setStyleSheet(self._btn_style_outline(BTN_PRIMARY))
        layout.addWidget(btn_add)

        btn_rem = QPushButton("Remover grupo")
        btn_rem.clicked.connect(self._remove_group)
        btn_rem.setStyleSheet(self._btn_text_danger_style())
        layout.addWidget(btn_rem)

        return panel

    # ── painel direito: atalhos ───────────────────────────────────────────────

    def _build_right_panel(self) -> QWidget:
        panel = QWidget()
        panel.setStyleSheet(f"background-color: {WINDOW_BG}; border: none;")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # header
        header = QWidget()
        header.setFixedHeight(46)
        header.setStyleSheet(f"background: {WINDOW_BG}; border-bottom: 1px solid {BORDER};")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(16, 8, 16, 8)
        header_layout.setSpacing(1)

        self._lbl_group_title = QLabel("—")
        self._lbl_group_title.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {TEXT_PRIMARY}; border: none;")
        header_layout.addWidget(self._lbl_group_title)

        self._lbl_group_count = QLabel("")
        self._lbl_group_count.setStyleSheet(f"font-size: 11px; color: {TEXT_MUTED}; border: none;")
        header_layout.addWidget(self._lbl_group_count)

        layout.addWidget(header)

        # lista de atalhos
        self._shortcut_list = QListWidget()
        self._shortcut_list.setStyleSheet(self._shortcut_list_style())
        self._shortcut_list.currentRowChanged.connect(self._on_shortcut_changed)
        layout.addWidget(self._shortcut_list)

        # rodapé de edição
        footer = QWidget()
        footer.setStyleSheet(f"background: {PANEL_BG}; border-top: 1px solid {BORDER};")
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(14, 10, 14, 12)
        footer_layout.setSpacing(8)

        # label + cancelar
        label_row = QHBoxLayout()
        label_row.setSpacing(0)
        self._lbl_add = QLabel("ADICIONAR ATALHO")
        self._lbl_add.setStyleSheet(f"font-size: 10px; color: {TEXT_MUTED}; letter-spacing: 1px; border: none;")
        label_row.addWidget(self._lbl_add)
        label_row.addStretch()
        self._btn_cancel = QPushButton("cancelar")
        self._btn_cancel.setVisible(False)
        self._btn_cancel.clicked.connect(self._clear_shortcut_fields)
        self._btn_cancel.setStyleSheet(self._btn_cancel_style())
        label_row.addWidget(self._btn_cancel)
        footer_layout.addLayout(label_row)

        # inputs
        inputs_row = QHBoxLayout()
        inputs_row.setSpacing(6)

        self._input_name = QLineEdit()
        self._input_name.setPlaceholderText("Nome")
        self._input_name.setFixedWidth(110)
        self._input_name.setStyleSheet(self._input_style())
        inputs_row.addWidget(self._input_name)

        self._input_path = QLineEdit()
        self._input_path.setPlaceholderText("Caminho do executável")
        self._input_path.setStyleSheet(self._input_style())
        inputs_row.addWidget(self._input_path)

        btn_browse = QPushButton("󰝰")   # fallback: ícone texto
        btn_browse.setText("📂")
        btn_browse.setFixedWidth(36)
        btn_browse.setToolTip("Procurar executável")
        btn_browse.clicked.connect(self._browse)
        btn_browse.setStyleSheet(self._btn_style(BTN_NEUTRAL))
        inputs_row.addWidget(btn_browse)

        self._btn_add_shortcut = QPushButton("+ Adicionar")
        self._btn_add_shortcut.clicked.connect(self._add_shortcut)
        self._btn_add_shortcut.setStyleSheet(self._btn_style(BTN_PRIMARY))
        inputs_row.addWidget(self._btn_add_shortcut)

        footer_layout.addLayout(inputs_row)
        layout.addWidget(footer)

        return panel

    # ── dados ─────────────────────────────────────────────────────────────────

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
            self._lbl_group_title.setText("—")
            self._lbl_group_count.setText("")
            return
        group = groups[group_index]
        shortcuts = group.get("shortcuts", [])
        self._lbl_group_title.setText(group["name"])
        n = len(shortcuts)
        self._lbl_group_count.setText(f"{n} atalho{'s' if n != 1 else ''}")
        for s in shortcuts:
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
                self._input_name.setText(Path(path).stem)

    def _add_shortcut(self):
        name = self._input_name.text().strip()
        path = self._input_path.text().strip()
        if not name or not path:
            return
        if self._editing_shortcut is not None:
            update_shortcut(self._selected_group, self._editing_shortcut, name, path)
        else:
            add_shortcut(self._selected_group, name, path)
        self._clear_shortcut_fields()
        self._load_shortcuts(self._selected_group)

    def _on_shortcut_changed(self, row: int):
        self._editing_shortcut = row if row >= 0 else None
        if self._editing_shortcut is None:
            self._clear_shortcut_fields()
            return
        groups = get_groups()
        shortcut = groups[self._selected_group]["shortcuts"][row]
        self._input_name.setText(shortcut["name"])
        self._input_path.setText(shortcut["path"])
        self._btn_add_shortcut.setText("✎ Atualizar")
        self._btn_add_shortcut.setStyleSheet(self._btn_style_outline(BTN_WARN))
        self._lbl_add.setText("EDITAR ATALHO")
        self._lbl_add.setStyleSheet(f"font-size: 10px; color: {BTN_WARN}; letter-spacing: 1px; border: none;")
        self._btn_cancel.setVisible(True)

    def _clear_shortcut_fields(self):
        self._input_name.clear()
        self._input_path.clear()
        self._editing_shortcut = None
        self._shortcut_list.clearSelection()
        self._btn_add_shortcut.setText("+ Adicionar")
        self._btn_add_shortcut.setStyleSheet(self._btn_style(BTN_PRIMARY))
        self._lbl_add.setText("ADICIONAR ATALHO")
        self._lbl_add.setStyleSheet(f"font-size: 10px; color: {TEXT_MUTED}; letter-spacing: 1px; border: none;")
        self._btn_cancel.setVisible(False)

    def _remove_shortcut(self):
        row = self._shortcut_list.currentRow()
        if row < 0:
            return
        remove_shortcut(self._selected_group, row)
        self._load_shortcuts(self._selected_group)

    # ── estilos ───────────────────────────────────────────────────────────────

    def _group_list_style(self) -> str:
        return f"""
            QListWidget {{
                background: transparent;
                border: none;
                outline: none;
                font-size: 13px;
                color: {TEXT_PRIMARY};
            }}
            QListWidget::item {{
                padding: 7px 10px;
                border-radius: 6px;
                color: {TEXT_LABEL};
            }}
            QListWidget::item:hover {{
                background: {SURFACE_HVR};
                color: {TEXT_PRIMARY};
            }}
            QListWidget::item:selected {{
                background: {SELECTED_HL}33;
                color: {SELECTED_HL};
                font-weight: 600;
            }}
        """

    def _shortcut_list_style(self) -> str:
        return f"""
            QListWidget {{
                background: transparent;
                border: none;
                outline: none;
                font-size: 12px;
                color: {TEXT_PRIMARY};
                padding: 6px 8px;
            }}
            QListWidget::item {{
                padding: 8px 10px;
                border-radius: 6px;
                color: {TEXT_PRIMARY};
            }}
            QListWidget::item:hover {{
                background: {SURFACE_HVR};
            }}
            QListWidget::item:selected {{
                background: {SURFACE};
                border: 1px solid {BORDER};
                color: {TEXT_PRIMARY};
            }}
        """

    def _input_style(self) -> str:
        return f"""
            QLineEdit {{
                background: {SURFACE};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border-color: {BTN_PRIMARY};
            }}
        """

    def _btn_style(self, bg: str) -> str:
        return f"""
            QPushButton {{
                background: {bg};
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 500;
            }}
            QPushButton:hover {{ background: {bg}cc; }}
            QPushButton:pressed {{ background: {bg}99; }}
        """

    def _btn_style_outline(self, color: str) -> str:
        return f"""
            QPushButton {{
                background: transparent;
                color: {color};
                border: 1px solid {color}66;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 500;
            }}
            QPushButton:hover {{ background: {color}1a; }}
            QPushButton:pressed {{ background: {color}33; }}
        """

    def _btn_text_danger_style(self) -> str:
        return f"""
            QPushButton {{
                background: transparent;
                color: {BTN_DANGER};
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
            }}
            QPushButton:hover {{ background: {BTN_DANGER}1a; }}
            QPushButton:pressed {{ background: {BTN_DANGER}33; }}
        """

    def _btn_cancel_style(self) -> str:
        return f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_MUTED};
                border: 1px solid {BORDER};
                border-radius: 5px;
                padding: 2px 8px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                color: {TEXT_PRIMARY};
                background: {SURFACE};
            }}
        """

    def closeEvent(self, event):
        event.accept()