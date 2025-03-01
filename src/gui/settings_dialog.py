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
        spacing = int(src.config.config.UI_SPACING.replace("px", ""))
        padding = int(src.config.config.UI_PADDING_NORMAL.replace("px", ""))
        layout.setSpacing(spacing)
        layout.setContentsMargins(padding, padding, padding, padding)

        # Create checkboxes
        self.prefix_checkbox = QCheckBox(STRINGS[self.parent.current_lang]['use_predefined_prefix'])
        self.prefix_checkbox.setObjectName("prefixCheckbox")
        self.prefix_checkbox.setChecked(src.config.config.USE_PREDEFINED_PREFIX)
        
        self.transcript_checkbox = QCheckBox(STRINGS[self.parent.current_lang]['use_transcript_text'])
        self.transcript_checkbox.setObjectName("transcriptCheckbox")
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
        font_family = src.config.config.UI_FONT_FAMILY
        font_size = src.config.config.UI_FONT_SIZE_NORMAL
        border_radius = src.config.config.UI_BORDER_RADIUS
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme['dialog_bg']};
                border-radius: {border_radius};
                font-family: {font_family};
            }}
            QCheckBox {{
                color: {theme['text']};
                font-size: {font_size};
                padding: 5px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {theme['input_border']};
                border-radius: 3px;
                background-color: {theme['input_bg']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {theme['button_bg']};
                border: 1px solid {theme['button_bg']};
            }}
            QCheckBox::indicator:checked:hover {{
                background-color: {theme['button_hover']};
                border: 1px solid {theme['button_hover']};
            }}
        """)
