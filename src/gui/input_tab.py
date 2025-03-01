from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
                           QPushButton)
from PyQt6.QtCore import Qt, QTimer
import src.config.config
from src.gui.lang import STRINGS
from src.gui.image_utils import (upload_image, clear_image, start_screenshot_dialog)

class InputTab(QWidget):
    """输入选项卡，用于管理自定义前缀后缀、图像处理等"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.ocr_enabled = False
        self.screenshot_enabled = False
        self.current_image_path = None
        self.init_ui()
        
    def init_ui(self):
        """初始化输入选项卡UI"""
        input_layout = QVBoxLayout(self)
        input_layout.setContentsMargins(5, 5, 5, 5)
        input_layout.setSpacing(3)
        
        # 自定义前缀/后缀
        prefix_suffix_layout = self._create_prefix_suffix_section()
        input_layout.addLayout(prefix_suffix_layout)
        
        # 图像功能区
        image_section = self._create_image_section()
        input_layout.addWidget(image_section)
        
    def _create_prefix_suffix_section(self):
        """创建前缀/后缀部分"""
        prefix_suffix_layout = QHBoxLayout()
        prefix_suffix_layout.setSpacing(5)
        
        # 前缀
        prefix_container = QWidget()
        prefix_container_layout = QVBoxLayout(prefix_container)
        prefix_container_layout.setContentsMargins(0, 0, 0, 0)
        prefix_container_layout.setSpacing(2)
        self.prefix_label = QLabel(STRINGS[self.parent.current_lang]['custom_prefix'])
        self.prefix_text = QTextEdit()
        self.prefix_text.setMaximumHeight(50)
        prefix_container_layout.addWidget(self.prefix_label)
        prefix_container_layout.addWidget(self.prefix_text)
        prefix_suffix_layout.addWidget(prefix_container)
        
        # 后缀
        suffix_container = QWidget()
        suffix_container_layout = QVBoxLayout(suffix_container)
        suffix_container_layout.setContentsMargins(0, 0, 0, 0)
        suffix_container_layout.setSpacing(2)
        self.suffix_label = QLabel(STRINGS[self.parent.current_lang]['custom_suffix'])
        self.suffix_text = QTextEdit()
        self.suffix_text.setMaximumHeight(50)
        suffix_container_layout.addWidget(self.suffix_label)
        suffix_container_layout.addWidget(self.suffix_text)
        prefix_suffix_layout.addWidget(suffix_container)
        
        return prefix_suffix_layout

    def _create_image_section(self):
        """创建图像处理部分"""
        image_section = QWidget()
        image_section_layout = QVBoxLayout(image_section)
        image_section_layout.setContentsMargins(0, 0, 0, 0)
        image_section_layout.setSpacing(3)
        
        # 图像按钮行
        image_buttons_layout = QHBoxLayout()
        image_buttons_layout.setSpacing(3)
        
        # OCR功能
        self.ocr_button = QPushButton(STRINGS[self.parent.current_lang]['ocr_screenshot'])
        self.ocr_button.setFixedHeight(28)
        self.ocr_button.clicked.connect(self.enable_ocr)
        image_buttons_layout.addWidget(self.ocr_button)
        
        # 图像上传功能
        self.image_upload_button = QPushButton(STRINGS[self.parent.current_lang]['image_upload'])
        self.image_upload_button.setFixedHeight(28)
        self.image_upload_button.clicked.connect(self.upload_image)
        image_buttons_layout.addWidget(self.image_upload_button)
        
        # 截图功能
        self.screenshot_button = QPushButton(STRINGS[self.parent.current_lang]['screenshot_capture'])
        self.screenshot_button.setFixedHeight(28)
        self.screenshot_button.clicked.connect(self.enable_screenshot)
        image_buttons_layout.addWidget(self.screenshot_button)
        
        # 清除图像按钮
        self.clear_image_button = QPushButton(STRINGS[self.parent.current_lang]['image_clear'])
        self.clear_image_button.setFixedHeight(28)
        self.clear_image_button.clicked.connect(self.clear_image)
        image_buttons_layout.addWidget(self.clear_image_button)
        
        image_section_layout.addLayout(image_buttons_layout)
        
        # 图像预览和OCR文本的水平布局
        image_ocr_layout = self._create_image_ocr_layout()
        image_section_layout.addLayout(image_ocr_layout)
        
        return image_section

    def _create_image_ocr_layout(self):
        """创建图像预览和OCR文本区域"""
        image_ocr_layout = QHBoxLayout()
        image_ocr_layout.setSpacing(5)
        
        # 图像预览
        image_preview_container = QWidget()
        image_preview_layout = QVBoxLayout(image_preview_container)
        image_preview_layout.setContentsMargins(0, 0, 0, 0)
        image_preview_layout.setSpacing(2)
        self.image_preview_label = QLabel(STRINGS[self.parent.current_lang]['image_preview'])
        self.image_display = QLabel()
        self.image_display.setMinimumSize(200, 80)
        self.image_display.setMaximumHeight(100)
        self.image_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_display.setStyleSheet("border: 1px solid #CCCCCC;")
        image_preview_layout.addWidget(self.image_preview_label)
        image_preview_layout.addWidget(self.image_display)
        image_ocr_layout.addWidget(image_preview_container)
        
        # OCR文本
        ocr_container = QWidget()
        ocr_layout = QVBoxLayout(ocr_container)
        ocr_layout.setContentsMargins(0, 0, 0, 0)
        ocr_layout.setSpacing(2)
        self.ocr_text_label = QLabel(STRINGS[self.parent.current_lang]['ocr_text'])
        self.ocr_text_edit = QTextEdit()
        self.ocr_text_edit.setMaximumHeight(100)
        ocr_layout.addWidget(self.ocr_text_label)
        ocr_layout.addWidget(self.ocr_text_edit)
        image_ocr_layout.addWidget(ocr_container)
        
        return image_ocr_layout
        
    def enable_ocr(self):
        """启用OCR功能"""
        self.ocr_enabled = False
        self.screenshot_enabled = False
        self.parent.showMinimized()
        
        # Small delay to allow window to minimize
        QTimer.singleShot(300, lambda: start_screenshot_dialog(self, "ocr"))

    def enable_screenshot(self):
        """启用截图功能"""
        self.screenshot_enabled = False
        self.ocr_enabled = False
        self.parent.showMinimized()
        
        # Small delay to allow window to minimize
        QTimer.singleShot(300, lambda: start_screenshot_dialog(self, "screenshot"))

    def upload_image(self):
        """上传图像"""
        upload_image(self)

    def clear_image(self):
        """清除图像"""
        clear_image(self)
        
    def get_prefix_text(self):
        """获取前缀文本"""
        return self.prefix_text.toPlainText()
        
    def get_suffix_text(self):
        """获取后缀文本"""
        return self.suffix_text.toPlainText()
    
    def get_ocr_text(self):
        """获取OCR文本"""
        return self.ocr_text_edit.toPlainText()
        
    def get_image_path(self):
        """获取当前图像路径"""
        return self.current_image_path
        
    def update_texts(self):
        """更新界面上的文本为当前语言"""
        self.prefix_label.setText(STRINGS[self.parent.current_lang]['custom_prefix'])
        self.suffix_label.setText(STRINGS[self.parent.current_lang]['custom_suffix'])
        self.ocr_button.setText(STRINGS[self.parent.current_lang]['ocr_screenshot'])
        self.ocr_text_label.setText(STRINGS[self.parent.current_lang]['ocr_text'])
        self.image_upload_button.setText(STRINGS[self.parent.current_lang]['image_upload'])
        self.screenshot_button.setText(STRINGS[self.parent.current_lang]['screenshot_capture'])
        self.clear_image_button.setText(STRINGS[self.parent.current_lang]['image_clear'])
        self.image_preview_label.setText(STRINGS[self.parent.current_lang]['image_preview'])
    
    def apply_theme(self, theme):
        """应用主题样式"""
        self.setStyleSheet(f"""
            QLabel {{
                font-size: 10pt;
                color: {theme['text']};
            }}
            QTextEdit {{
                font-size: 10pt;
                padding: 4px;
                border: 1px solid {theme['input_border']};
                border-radius: 4px;
                background-color: {theme['input_bg']};
                color: {theme['text']};
            }}
            QPushButton {{
                background-color: {theme['button_bg']};
                color: {theme['button_text']};
                padding: 8px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {theme['button_hover']};
            }}
        """)