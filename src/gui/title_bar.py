from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt
from src.gui.lang import STRINGS
import src.config.config

class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def create_title_button(self, text, callback):
        """Create a title bar button with common properties"""
        button = QPushButton(text)
        button.setFixedSize(30, 30)
        button.setObjectName("titleButton")
        button.clicked.connect(callback)
        return button

    def init_ui(self):
        title_layout = QHBoxLayout(self)
        title_layout.setContentsMargins(10, 5, 10, 5)

        # 标题文本
        self.title_label = QLabel(STRINGS[self.parent.current_lang]['window_title'])
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()

        # Title bar buttons
        min_button = self.create_title_button("－", self.parent.showMinimized)
        close_button = self.create_title_button("✕", self.parent.close)
        title_layout.addWidget(min_button)
        title_layout.addWidget(close_button)

    def update_title(self):
        self.title_label.setText(STRINGS[self.parent.current_lang]['window_title'])

    def apply_theme(self):
        theme = src.config.config.THEMES[self.parent.current_theme]
        self.setStyleSheet(f"""
            #titleButton {{
                background-color: transparent;
                border: none;
                color: {theme['text']};
                font-size: 16px;
            }}
            #titleButton:hover {{
                background-color: {theme['title_button_hover']};
                color: white;
            }}
        """)
