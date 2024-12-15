from PyQt6.QtWidgets import QDialog, QVBoxLayout, QCheckBox
from src.gui.lang import STRINGS
import src.config.config

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle(STRINGS[self.parent.current_lang]['settings_title'])
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Create checkboxes
        self.prefix_checkbox = QCheckBox(STRINGS[self.parent.current_lang]['use_predefined_prefix'])
        self.prefix_checkbox.setChecked(src.config.config.USE_PREDEFINED_PREFIX)
        
        self.transcript_checkbox = QCheckBox(STRINGS[self.parent.current_lang]['use_transcript_text'])
        self.transcript_checkbox.setChecked(src.config.config.USE_TRANSCRIPT_TEXT)

        # Add checkboxes to layout
        layout.addWidget(self.prefix_checkbox)
        layout.addWidget(self.transcript_checkbox)

        self.setLayout(layout)

        # Connect signals
        self.prefix_checkbox.stateChanged.connect(self.update_settings)
        self.transcript_checkbox.stateChanged.connect(self.update_settings)

    def update_settings(self):
        src.config.config.USE_PREDEFINED_PREFIX = self.prefix_checkbox.isChecked()
        src.config.config.USE_TRANSCRIPT_TEXT = self.transcript_checkbox.isChecked()

    def apply_theme(self):
        theme = src.config.config.THEMES[self.parent.current_theme]
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme['dialog_bg']};
            }}
            QCheckBox {{
                color: {theme['text']};
            }}
        """)
