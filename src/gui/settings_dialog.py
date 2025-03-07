from PyQt6.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QPushButton, QHBoxLayout, QLabel
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

        # 基础设置部分
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
        
        # 添加分隔线
        separator_line = QLabel()
        separator_line.setFixedHeight(1)
        separator_line.setStyleSheet("background-color: #cccccc;")
        layout.addWidget(separator_line)
        
        # 连续对话部分
        # 添加连续对话选项
        self.continuous_dialogue_checkbox = QCheckBox(STRINGS[self.parent.current_lang]['enable_continuous_dialogue'])
        self.continuous_dialogue_checkbox.setObjectName("continuousDialogueCheckbox")
        self.continuous_dialogue_checkbox.setChecked(src.config.config.ENABLE_CONTINUOUS_DIALOGUE)
        layout.addWidget(self.continuous_dialogue_checkbox)
        
        # 添加重置按钮
        reset_buttons_layout = QHBoxLayout()
        
        self.reset_context_button = QPushButton(STRINGS[self.parent.current_lang]['reset_dialogue_context'])
        self.reset_context_button.setObjectName("resetContextButton")
        self.reset_context_button.setEnabled(src.config.config.ENABLE_CONTINUOUS_DIALOGUE)
        reset_buttons_layout.addWidget(self.reset_context_button)
        
        self.reset_position_button = QPushButton(STRINGS[self.parent.current_lang]['reset_position'])
        self.reset_position_button.setObjectName("resetPositionButton")
        self.reset_position_button.setEnabled(src.config.config.ENABLE_CONTINUOUS_DIALOGUE)
        reset_buttons_layout.addWidget(self.reset_position_button)
        
        layout.addLayout(reset_buttons_layout)

        self.setLayout(layout)

        # Connect signals
        self.prefix_checkbox.stateChanged.connect(self.update_settings)
        self.transcript_checkbox.stateChanged.connect(self.update_settings)
        self.continuous_dialogue_checkbox.stateChanged.connect(self.update_settings)
        self.reset_context_button.clicked.connect(self.reset_dialogue_context)
        self.reset_position_button.clicked.connect(self.reset_file_position)

    def update_settings(self):
        src.config.config.USE_PREDEFINED_PREFIX = self.prefix_checkbox.isChecked()
        src.config.config.USE_TRANSCRIPT_TEXT = self.transcript_checkbox.isChecked()
        src.config.config.ENABLE_CONTINUOUS_DIALOGUE = self.continuous_dialogue_checkbox.isChecked()
        
        # 更新按钮状态
        self.reset_context_button.setEnabled(src.config.config.ENABLE_CONTINUOUS_DIALOGUE)
        self.reset_position_button.setEnabled(src.config.config.ENABLE_CONTINUOUS_DIALOGUE)

    def reset_dialogue_context(self):
        """重置对话上下文，将清空所有历史消息"""
        if hasattr(self.parent, 'content_area'):
            # 清空对话历史记录
            if hasattr(self.parent.content_area, 'dialogue_history'):
                self.parent.content_area.dialogue_history = []
            
            # 设置状态消息
            self.parent.content_area.output_area.set_status(STRINGS[self.parent.current_lang]['reset_dialogue_context'])
        self.accept()

    def reset_file_position(self):
        """重置文件位置，将从头开始读取"""
        if hasattr(self.parent, 'content_area'):
            # 重置文件位置跟踪
            src.config.config.TRANSCRIPT_POSITION = {}
            
            # 设置状态消息
            self.parent.content_area.output_area.set_status(STRINGS[self.parent.current_lang]['reset_position_success'])
        self.accept()

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
            QPushButton {{
                background-color: {theme['button_bg']};
                color: {theme['button_text']};
                border-radius: {border_radius};
                padding: 5px;
                font-size: {font_size};
            }}
            QPushButton:hover {{
                background-color: {theme['button_hover']};
            }}
            QPushButton:disabled {{
                background-color: {theme['input_border']};
                color: {theme['text_secondary']};
            }}
        """)
