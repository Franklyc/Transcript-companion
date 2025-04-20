from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                           QTextBrowser)
from PyQt6.QtCore import pyqtSignal
import os
import datetime
import src.config.config
from src.gui.lang import STRINGS
import src.gui.utils
import src.gui.prefix
from src.gui.markdown_viewer import render_markdown, append_markdown_text

class OutputArea(QWidget):
    """输出区域，用于显示和导出模型回答"""
    
    export_requested = pyqtSignal()
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.raw_output_text = ""
        self.init_ui()
        
    def init_ui(self):
        """初始化输出区域UI"""
        bottom_layout = QVBoxLayout(self)
        spacing = int(src.config.config.UI_SPACING.replace("px", ""))
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(spacing)
        
        # 状态标签
        self.status_label = QLabel()
        self.status_label.setObjectName("status_label")
        self.status_label.setMaximumHeight(40)
        bottom_layout.addWidget(self.status_label)
        
        # 输出文本区域 - 使用QTextBrowser以支持显示HTML/Markdown
        self.output_label = QLabel(STRINGS[self.parent.current_lang]['output_result'])
        self.output_label.setObjectName("outputLabel")
        
        # 创建一个带有标签的水平布局
        output_header_layout = QHBoxLayout()
        output_header_layout.setSpacing(spacing)
        output_header_layout.addWidget(self.output_label)
        
        # 添加显示模式切换按钮
        self.toggle_markdown_button = QPushButton("Markdown")
        self.toggle_markdown_button.setObjectName("markdownToggleButton")
        self.toggle_markdown_button.setCheckable(True)
        self.toggle_markdown_button.setChecked(True)
        self.toggle_markdown_button.clicked.connect(self.toggle_markdown_display)
        self.toggle_markdown_button.setFixedWidth(120)
        self.toggle_markdown_button.setFixedHeight(28)
        output_header_layout.addStretch()
        output_header_layout.addWidget(self.toggle_markdown_button)
        
        bottom_layout.addLayout(output_header_layout)
        
        # 使用QTextBrowser显示输出内容
        self.output_text = QTextBrowser()
        self.output_text.setObjectName("outputBrowser")
        self.output_text.setOpenExternalLinks(True)
        bottom_layout.addWidget(self.output_text)
        
        # 底部按钮布局
        buttons_layout = self._create_bottom_buttons()
        bottom_layout.addLayout(buttons_layout)
        
    def _create_bottom_buttons(self):
        """创建底部按钮区域"""
        buttons_layout = QHBoxLayout()
        spacing = int(src.config.config.UI_SPACING.replace("px", ""))
        buttons_layout.setSpacing(spacing)

        # 复制/获取回答按钮
        self.copy_button = QPushButton(STRINGS[self.parent.current_lang]['copy_and_get_answer'])
        self.copy_button.setObjectName("copyButton")
        buttons_layout.addWidget(self.copy_button)

        # 停止按钮 (初始隐藏)
        self.stop_button = QPushButton(STRINGS[self.parent.current_lang]['stop_generating']) # Add 'stop_generating' to STRINGS
        self.stop_button.setObjectName("stopButton")
        self.stop_button.setVisible(False) # Initially hidden
        buttons_layout.addWidget(self.stop_button)

        # 导出按钮
        self.export_button = QPushButton(STRINGS[self.parent.current_lang]['export_conversation'])
        self.export_button.setObjectName("exportButton")
        self.export_button.clicked.connect(self.export_conversation)
        buttons_layout.addWidget(self.export_button)

        return buttons_layout

    def append_text(self, text):
        """API调用将使用此方法来添加文本"""
        self.raw_output_text = append_markdown_text(
            self.output_text,
            self.raw_output_text,
            text,
            self.toggle_markdown_button.isChecked(),
            self.parent.current_theme == "dark"
        )

    def clear_output(self):
        """清空输出区域"""
        self.output_text.clear()
        self.raw_output_text = ""

    def toggle_markdown_display(self):
        """切换Markdown和纯文本显示模式"""
        is_markdown = self.toggle_markdown_button.isChecked()
        if is_markdown:
            self.toggle_markdown_button.setText("Markdown")
            # 将原始文本转换为HTML并显示
            render_markdown(self.output_text, self.raw_output_text, self.parent.current_theme == "dark")
        else:
            self.toggle_markdown_button.setText(STRINGS[self.parent.current_lang]['show_source'])
            # 显示原始文本
            self.output_text.setPlainText(self.raw_output_text)

    def export_conversation(self, folder_path="", prefix_text="", suffix_text="", image_path=None, ocr_text=""):
        """导出当前对话"""
        self.export_requested.emit()
        
    def set_status(self, message, is_error=False):
        """设置状态消息"""
        self.status_label.setText(message)
        status_color = "status_error" if is_error else "status_success"
        theme = src.config.config.THEMES[self.parent.current_theme]
        self.status_label.setStyleSheet(f"color: {theme[status_color]};")
    
    def update_texts(self):
        """更新界面上的文本为当前语言"""
        self.output_label.setText(STRINGS[self.parent.current_lang]['output_result'])
        self.copy_button.setText(STRINGS[self.parent.current_lang]['copy_and_get_answer'])
        self.stop_button.setText(STRINGS[self.parent.current_lang]['stop_generating'])
        self.export_button.setText(STRINGS[self.parent.current_lang]['export_conversation'])

        # 更新Markdown切换按钮文本
        if not self.toggle_markdown_button.isChecked():
            self.toggle_markdown_button.setText(STRINGS[self.parent.current_lang]['show_source'])
        else:
            self.toggle_markdown_button.setText("Markdown")
    
    def apply_theme(self, theme):
        """应用主题样式"""
        font_family = src.config.config.UI_FONT_FAMILY
        font_size_normal = src.config.config.UI_FONT_SIZE_NORMAL
        font_size_large = src.config.config.UI_FONT_SIZE_LARGE
        border_radius = src.config.config.UI_BORDER_RADIUS
        padding_small = src.config.config.UI_PADDING_SMALL
        padding_normal = src.config.config.UI_PADDING_NORMAL
        
        self.setStyleSheet(f"""
            QWidget {{
                font-family: {font_family};
            }}
            QLabel {{
                font-size: {font_size_normal};
                color: {theme['text']};
            }}
            #outputLabel {{
                font-weight: bold;
            }}
            #outputBrowser {{
                font-size: {font_size_large};
                padding: {padding_small};
                border: 1px solid {theme['input_border']};
                border-radius: {border_radius};
                background-color: {theme['input_bg']};
                color: {theme['text']};
            }}
            #markdownToggleButton {{
                background-color: {theme['button_bg']};
                color: {theme['button_text']};
                padding: {padding_small};
                border-radius: {border_radius};
                font-size: {font_size_normal};
            }}
            #markdownToggleButton:hover {{
                background-color: {theme['button_hover']};
            }}
            #copyButton, #exportButton, #stopButton {{
                background-color: {theme['button_bg']};
                color: {theme['button_text']};
                padding: {padding_normal};
                border-radius: {border_radius};
                font-size: {font_size_large};
                min-height: 36px;
            }}
            #copyButton:hover, #exportButton:hover, #stopButton:hover {{
                background-color: {theme['button_hover']};
            }}
            #stopButton {{
                 background-color: {theme['button_danger_bg']}; /* Use a danger color */
            }}
             #stopButton:hover {{
                 background-color: {theme['button_danger_hover']};
            }}
            #exportButton {{
                background-color: {theme['button_success_bg']};
            }}
            #exportButton:hover {{
                background-color: {theme['button_success_hover']};
            }}
            #status_label {{
                font-size: {font_size_normal};
                padding: {padding_small};
            }}
        """)