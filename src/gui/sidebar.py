from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt
from src.gui.lang import STRINGS
import src.config.config

class Sidebar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def create_sidebar_button(self, text, object_name, size=(40, 40), callback=None):
        """Create a sidebar button with common properties"""
        button = QPushButton(text)
        button.setFixedSize(*size)
        button.setObjectName(object_name)
        if callback:
            button.clicked.connect(callback)
        return button

    def init_ui(self):
        self.setFixedWidth(50)
        self.setObjectName("sidebar")  # 添加这行来设置ObjectName
        sidebar_layout = QVBoxLayout(self)
        sidebar_layout.setContentsMargins(5, 5, 5, 5)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Sidebar buttons
        sidebar_buttons = [
            ("🀄" if self.parent.current_lang == 'zh' else "🔤", "langButton", self.parent.toggle_language),
            ("🌙" if self.parent.current_theme == "light" else "☀️", "themeButton", self.parent.toggle_theme),
            ("❓", "sidebarButton", self.parent.show_help),
            ("⚙️", "sidebarButton", self.parent.show_settings),
            ("🗑️", "sidebarButton", self.parent.clear_content),
            ("🔄", "sidebarButton", lambda: self.parent.update_model_list(True)),
        ]

        for text, obj_name, callback in sidebar_buttons:
            button = self.create_sidebar_button(text, obj_name, callback=callback)
            sidebar_layout.addWidget(button)
            if obj_name == "langButton":
                self.lang_button = button
            elif obj_name == "themeButton":
                self.theme_button = button

        sidebar_layout.addStretch()

    def apply_theme(self):
        theme = src.config.config.THEMES[self.parent.current_theme]
        self.setStyleSheet(f"""
            QWidget#sidebar {{
                background-color: {theme['sidebar_bg']};
                border-right: 1px solid {theme['input_border']};
            }}
            #themeButton {{
                background-color: transparent;
                border: none;
                color: {theme['text']};
                font-size: 16px;
                padding: 4px;
            }}
            #themeButton:hover {{
                background-color: {theme['input_border']};
            }}
            #langButton {{
                background-color: transparent;
                border: none;
                color: {theme['text']};
                font-size: 16px;
                padding: 4px;
            }}
            #langButton:hover {{
                background-color: {theme['input_border']};
            }}
            #sidebarButton {{
                background-color: transparent;
                border: none;
                color: {theme['text']};
                font-size: 16px;
                padding: 4px;
            }}
            #sidebarButton:hover {{
                background-color: {theme['input_border']};
                border-radius: 4px;
            }}
        """)
