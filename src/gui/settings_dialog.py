from PyQt6.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QPushButton, QHBoxLayout, QLabel, QSlider, QLineEdit
from PyQt6.QtCore import Qt
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
        
        # 添加分隔线
        separator_line2 = QLabel()
        separator_line2.setFixedHeight(1)
        separator_line2.setStyleSheet("background-color: #cccccc;")
        layout.addWidget(separator_line2)
        
        # Gemini搜索功能部分
        self.gemini_search_checkbox = QCheckBox(STRINGS[self.parent.current_lang].get('enable_gemini_search', 'Enable Google Search for Gemini models'))
        self.gemini_search_checkbox.setObjectName("geminiSearchCheckbox")
        self.gemini_search_checkbox.setChecked(src.config.config.ENABLE_GEMINI_SEARCH)
        layout.addWidget(self.gemini_search_checkbox)
        
        # 添加分隔线
        separator_line3 = QLabel()
        separator_line3.setFixedHeight(1)
        separator_line3.setStyleSheet("background-color: #cccccc;")
        layout.addWidget(separator_line3)
        
        # Gemini思考预算部分
        thinking_budget_title = QLabel(STRINGS[self.parent.current_lang].get('gemini_thinking_budget_title', 'Gemini Thinking Budget Settings'))
        thinking_budget_title.setObjectName("thinkingBudgetTitle")
        layout.addWidget(thinking_budget_title)
        
        # 添加说明文本
        thinking_budget_description = QLabel(STRINGS[self.parent.current_lang].get('gemini_thinking_budget_description', 'Only supported for gemini-2.5-flash-preview-04-17 model'))
        thinking_budget_description.setObjectName("thinkingBudgetDescription")
        thinking_budget_description.setStyleSheet("font-size: 9pt; color: #888888;")
        layout.addWidget(thinking_budget_description)
        
        # 创建水平布局存放滑动条和输入框
        thinking_budget_layout = QHBoxLayout()
        
        # 添加标签
        self.thinking_budget_label = QLabel(STRINGS[self.parent.current_lang].get('gemini_thinking_budget_label', 'Thinking Budget (0-24576):'))
        self.thinking_budget_label.setObjectName("thinkingBudgetLabel")
        thinking_budget_layout.addWidget(self.thinking_budget_label)
        
        # 添加滑动条
        self.thinking_budget_slider = QSlider(Qt.Orientation.Horizontal)
        self.thinking_budget_slider.setObjectName("thinkingBudgetSlider")
        self.thinking_budget_slider.setMinimum(0)
        self.thinking_budget_slider.setMaximum(24576)
        self.thinking_budget_slider.setValue(src.config.config.GEMINI_THINKING_BUDGET)
        self.thinking_budget_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.thinking_budget_slider.setTickInterval(4096)
        thinking_budget_layout.addWidget(self.thinking_budget_slider)
        
        # 添加数值输入框
        self.thinking_budget_input = QLineEdit(str(src.config.config.GEMINI_THINKING_BUDGET))
        self.thinking_budget_input.setObjectName("thinkingBudgetInput")
        self.thinking_budget_input.setFixedWidth(60)
        thinking_budget_layout.addWidget(self.thinking_budget_input)
        
        # 将水平布局添加到主布局
        layout.addLayout(thinking_budget_layout)

        self.setLayout(layout)

        # Connect signals
        self.prefix_checkbox.stateChanged.connect(self.update_settings)
        self.transcript_checkbox.stateChanged.connect(self.update_settings)
        self.continuous_dialogue_checkbox.stateChanged.connect(self.update_settings)
        self.gemini_search_checkbox.stateChanged.connect(self.update_settings)
        self.reset_context_button.clicked.connect(self.reset_dialogue_context)
        self.reset_position_button.clicked.connect(self.reset_file_position)
        
        # Connect thinking budget signals
        self.thinking_budget_slider.valueChanged.connect(self.update_thinking_budget_from_slider)
        self.thinking_budget_input.editingFinished.connect(self.update_thinking_budget_from_input)

    def update_settings(self):
        src.config.config.USE_PREDEFINED_PREFIX = self.prefix_checkbox.isChecked()
        src.config.config.USE_TRANSCRIPT_TEXT = self.transcript_checkbox.isChecked()
        src.config.config.ENABLE_CONTINUOUS_DIALOGUE = self.continuous_dialogue_checkbox.isChecked()
        src.config.config.ENABLE_GEMINI_SEARCH = self.gemini_search_checkbox.isChecked()
        
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
        
    def update_thinking_budget_from_slider(self, value):
        """从滑动条更新思考预算值"""
        src.config.config.GEMINI_THINKING_BUDGET = value
        self.thinking_budget_input.setText(str(value))
        
        if hasattr(self.parent, 'content_area'):
            status_message = STRINGS[self.parent.current_lang].get('gemini_thinking_budget_saved', 'Gemini thinking budget updated to: {0}').format(value)
            self.parent.content_area.output_area.set_status(status_message)
            
    def update_thinking_budget_from_input(self):
        """从输入框更新思考预算值"""
        try:
            value = int(self.thinking_budget_input.text())
            # 确保值在有效范围内
            if value < 0:
                value = 0
            elif value > 24576:
                value = 24576
                
            src.config.config.GEMINI_THINKING_BUDGET = value
            self.thinking_budget_slider.setValue(value)
            
            if hasattr(self.parent, 'content_area'):
                status_message = STRINGS[self.parent.current_lang].get('gemini_thinking_budget_saved', 'Gemini thinking budget updated to: {0}').format(value)
                self.parent.content_area.output_area.set_status(status_message)
        except ValueError:
            # 如果输入无效，恢复为当前值
            self.thinking_budget_input.setText(str(src.config.config.GEMINI_THINKING_BUDGET))

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
            QLabel#thinkingBudgetTitle {{
                color: {theme['text']};
                font-weight: bold;
                margin-top: 5px;
            }}
            QLabel#thinkingBudgetDescription {{
                color: {theme['text_secondary']};
                font-size: 9pt;
            }}
            QSlider::groove:horizontal {{
                border: 1px solid {theme['input_border']};
                height: 8px;
                background: {theme['input_bg']};
                margin: 2px 0;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {theme['button_bg']};
                border: 1px solid {theme['button_bg']};
                width: 18px;
                height: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {theme['button_hover']};
                border: 1px solid {theme['button_hover']};
            }}
            QSlider::add-page:horizontal {{
                background: {theme['input_bg']};
                border-radius: 4px;
            }}
            QSlider::sub-page:horizontal {{
                background: {theme['button_bg']};
                border-radius: 4px;
            }}
        """)
