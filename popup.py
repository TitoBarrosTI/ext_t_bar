# popup.py
import subprocess
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                                QPushButton, QLabel, QApplication, QGridLayout)
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QIcon

from winapi import get_taskbar_rect, extract_icon
from config import get_groups

PADDING      = 8
MARGIN       = 0
HEADER_HEIGHT = 22
CAT_HEIGHT   = 28
ICON_SIZE    = 38

HEADER_BG  = "#4f8ef7"
HEADER_TEXT = "#ffffff"
POPUP_BG   = "#2b2b2b"
BTN_BG     = "#3c3c3c"
BTN_HOVER  = "#505050"
CAT_BG     = "#222222"
CAT_ACTIVE = "#4f8ef7"
WARN_COLOR = "#e06c75"

class PopupLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self._groups = get_groups()
        self._active = 0
        self._icon_buttons = QGridLayout()
        self._setup_window()
        self._build_ui()
        self._position()

    def _setup_window(self):
        self.setWindowFlags(
            Qt.Popup |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )
        self.setStyleSheet(f"background-color: {POPUP_BG}; border-radius: 8px;")

    def _build_ui(self):
        self._root = QGridLayout()
        self._root.setContentsMargins(0, 0, 0, 0)
        self._root.setSpacing(0)

        self._root.addWidget(self._build_header())
        self._root.addWidget(self._build_categories())

        self._icons_container = QWidget()
        self._icons_row = QGridLayout(self._icons_container)
        self._icons_row.setContentsMargins(PADDING, PADDING, PADDING, PADDING)
        self._icons_row.setSpacing(6)
        self._root.addWidget(self._icons_container)

        self.setLayout(self._root)
        self._load_icons(0)
        self.adjustSize()

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setFixedHeight(HEADER_HEIGHT)
        header.setStyleSheet(f"""
            background-color: {HEADER_BG};
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
        """)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(10, 0, 6, 0)

        title = QLabel("ExtTaskBar")
        title.setStyleSheet(f"color: {HEADER_TEXT}; font-size: 11px; font-weight: bold; background: transparent;")
        title.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        btn_cfg = QPushButton("⚙")
        btn_cfg.setFixedSize(20, 20)
        btn_cfg.setToolTip("Configurações")
        btn_cfg.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {HEADER_TEXT};
                border: none;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: rgba(255,255,255,40);
                border-radius: 4px;
            }}
        """)
        btn_cfg.clicked.connect(self._open_config)

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(btn_cfg)

        return header

    def _build_categories(self) -> QWidget:
        self._cat_widget = QWidget()
        self._cat_widget.setFixedHeight(CAT_HEIGHT)
        self._cat_widget.setStyleSheet(f"background-color: {CAT_BG};")

        self._cat_layout = QHBoxLayout(self._cat_widget)
        self._cat_layout.setContentsMargins(PADDING, 0, PADDING, 0)
        self._cat_layout.setSpacing(4)

        self._cat_buttons = []
        for i, group in enumerate(self._groups):
            btn = QPushButton(group["name"])
            btn.setFixedHeight(20)
            btn.setStyleSheet(self._cat_style(i == 0))
            btn.enterEvent = lambda e, idx=i: self._on_cat_hover(idx)
            self._cat_layout.addWidget(btn)
            self._cat_buttons.append(btn)

        self._cat_layout.addStretch()
        return self._cat_widget

    def _on_cat_hover(self, index: int):
        if index == self._active:
            return
        self._active = index
        for i, btn in enumerate(self._cat_buttons):
            btn.setStyleSheet(self._cat_style(i == index))
        self._load_icons(index)
        self.adjustSize()

    def _load_icons(self, group_index: int):
        while self._icons_row.count():
            item = self._icons_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self._groups:
            return        
        
        shortcuts = self._groups[group_index].get("shortcuts", [])
        
        MAX_COLS = 6
        row = col = 0

        for shortcut in shortcuts:
            btn = QPushButton()
            btn.setFixedSize(ICON_SIZE, ICON_SIZE)

            pixmap = extract_icon(shortcut["path"])

            if pixmap:
                btn.setIcon(QIcon(pixmap))
                btn.setIconSize(pixmap.size())
                btn.setToolTip(shortcut["name"])
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {BTN_BG};
                        border: none;
                        border-radius: 6px;
                    }}
                    QPushButton:hover {{
                        background-color: {BTN_HOVER};
                    }}
                """)
            else:
                btn.setText("⚠")
                btn.setToolTip(f"Não encontrado: {shortcut['path']}")
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {BTN_BG};
                        color: {WARN_COLOR};
                        border: none;
                        border-radius: 6px;
                        font-size: 16px;
                    }}
                    QPushButton:hover {{
                        background-color: {BTN_HOVER};
                    }}
                """)

            btn.clicked.connect(lambda checked, p=shortcut["path"]: self._launch(p))
            self._icons_row.addWidget(btn, row, col)
            
            col += 1
            if col >= MAX_COLS:
                col = 0
                row += 1

    def _launch(self, path: str):
        subprocess.Popen(path)
        self.close()

    def _open_config(self):
        from config_window import ConfigWindow
        self._cfg = ConfigWindow()
        self._cfg.show()
        self.hide()

    def _cat_style(self, active: bool) -> str:
        bg = CAT_ACTIVE if active else "transparent"
        return f"""
            QPushButton {{
                background-color: {bg};
                color: {HEADER_TEXT};
                border: none;
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {CAT_ACTIVE};
            }}
        """

    def _position(self):
        cursor = QCursor.pos()
        taskbar = get_taskbar_rect()
        self.adjustSize()
        popup_width = self.sizeHint().width()
        x = cursor.x() - popup_width // 2
        y = taskbar.top - self.sizeHint().height() - MARGIN
        self.move(x, y)

    def closeEvent(self, event):
        # naum mata o app - daemon continua rodando
        event.accept()