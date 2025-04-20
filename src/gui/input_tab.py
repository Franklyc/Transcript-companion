from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
                           QPushButton, QScrollArea)
from PyQt6.QtCore import Qt, QTimer
import src.config.config
from src.gui.lang import STRINGS
from src.gui.image_utils import (upload_image, clear_image, start_screenshot_dialog, take_fullscreen_screenshot)

class InputTab(QWidget):
    """输入选项卡，用于管理自定义前缀后缀、图像处理等"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.ocr_enabled = False
        self.screenshot_enabled = False
        self.image_paths = []  # 存储图像路径的列表
        self.init_ui()
        
    def init_ui(self):
        """初始化输入选项卡UI"""
        input_layout = QVBoxLayout(self)
        spacing = int(src.config.config.UI_SPACING.replace("px", ""))
        input_layout.setContentsMargins(5, 5, 5, 5)
        input_layout.setSpacing(spacing)
        
        # 自定义前缀/后缀
        prefix_suffix_layout = self._create_prefix_suffix_section()
        input_layout.addLayout(prefix_suffix_layout)
        
        # 图像功能区
        image_section = self._create_image_section()
        input_layout.addWidget(image_section)
        
    def _create_prefix_suffix_section(self):
        """创建前缀/后缀部分"""
        prefix_suffix_layout = QHBoxLayout()
        spacing = int(src.config.config.UI_SPACING.replace("px", ""))
        prefix_suffix_layout.setSpacing(spacing)
        
        # 前缀
        prefix_container = QWidget()
        prefix_container_layout = QVBoxLayout(prefix_container)
        prefix_container_layout.setContentsMargins(0, 0, 0, 0)
        prefix_container_layout.setSpacing(2)
        self.prefix_label = QLabel(STRINGS[self.parent.current_lang]['custom_prefix'])
        self.prefix_text = QTextEdit()
        self.prefix_text.setMaximumHeight(50)
        self.prefix_text.setObjectName("prefixTextEdit")
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
        self.suffix_text.setObjectName("suffixTextEdit")
        suffix_container_layout.addWidget(self.suffix_label)
        suffix_container_layout.addWidget(self.suffix_text)
        prefix_suffix_layout.addWidget(suffix_container)
        
        return prefix_suffix_layout

    def _create_image_section(self):
        """创建图像处理部分"""
        image_section = QWidget()
        image_section_layout = QVBoxLayout(image_section)
        spacing = int(src.config.config.UI_SPACING.replace("px", ""))
        image_section_layout.setContentsMargins(0, 0, 0, 0)
        image_section_layout.setSpacing(spacing)
        
        # 图像按钮行
        image_buttons_layout = self._create_image_buttons_layout()
        image_section_layout.addLayout(image_buttons_layout)
        
        # 图像预览和OCR文本的水平布局
        image_ocr_layout = self._create_image_ocr_layout()
        image_section_layout.addLayout(image_ocr_layout)
        
        return image_section

    def _create_image_buttons_layout(self):
        """创建图像按钮行"""
        image_buttons_layout = QHBoxLayout()
        spacing = int(src.config.config.UI_SPACING.replace("px", ""))
        image_buttons_layout.setSpacing(spacing)
        
        # OCR功能
        self.ocr_button = QPushButton(STRINGS[self.parent.current_lang]['ocr_screenshot'])
        self.ocr_button.setObjectName("ocrButton")
        self.ocr_button.setFixedHeight(28)
        self.ocr_button.clicked.connect(self.enable_ocr)
        image_buttons_layout.addWidget(self.ocr_button)
        
        # 图像上传功能
        self.image_upload_button = QPushButton(STRINGS[self.parent.current_lang]['image_upload'])
        self.image_upload_button.setObjectName("uploadButton")
        self.image_upload_button.setFixedHeight(28)
        self.image_upload_button.clicked.connect(self.upload_image)
        image_buttons_layout.addWidget(self.image_upload_button)
        
        # 区域截图功能
        self.screenshot_button = QPushButton(STRINGS[self.parent.current_lang]['screenshot_capture'])
        self.screenshot_button.setObjectName("screenshotButton")
        self.screenshot_button.setFixedHeight(28)
        self.screenshot_button.clicked.connect(self.enable_screenshot)
        image_buttons_layout.addWidget(self.screenshot_button)
        
        # 全屏截图功能
        self.fullscreen_button = QPushButton(STRINGS[self.parent.current_lang]['fullscreen_capture'])
        self.fullscreen_button.setObjectName("fullscreenButton")
        self.fullscreen_button.setFixedHeight(28)
        self.fullscreen_button.clicked.connect(self.take_fullscreen)
        image_buttons_layout.addWidget(self.fullscreen_button)
        
        # 清除图像按钮
        self.clear_image_button = QPushButton(STRINGS[self.parent.current_lang]['clear_all_images'])
        self.clear_image_button.setObjectName("clearButton")
        self.clear_image_button.setFixedHeight(28)
        self.clear_image_button.clicked.connect(lambda: clear_image(self))
        image_buttons_layout.addWidget(self.clear_image_button)
        
        return image_buttons_layout

    def _create_image_ocr_layout(self):
        """创建图像预览和OCR文本区域"""
        image_ocr_layout = QHBoxLayout()
        spacing = int(src.config.config.UI_SPACING.replace("px", ""))
        image_ocr_layout.setSpacing(spacing)
        
        # 图像预览容器（带滚动区域）
        image_preview_container = QWidget()
        image_preview_layout = QVBoxLayout(image_preview_container)
        image_preview_layout.setContentsMargins(0, 0, 0, 0)
        image_preview_layout.setSpacing(5)
        
        # 图像预览标签
        self.image_preview_label = QLabel(STRINGS[self.parent.current_lang]['image_preview'])
        image_preview_layout.addWidget(self.image_preview_label)
        
        # 滚动区域用于显示多张图片
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(120)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 创建图像容器
        self.images_container = QWidget()
        self.images_container.setObjectName("imagesContainer") # 添加 objectName
        self.images_layout = QVBoxLayout(self.images_container)
        self.images_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.images_layout.setSpacing(10)
        
        # 初始显示
        initial_label = QLabel(STRINGS[self.parent.current_lang]['image_preview'])
        initial_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.images_layout.addWidget(initial_label)
        
        scroll_area.setWidget(self.images_container)
        image_preview_layout.addWidget(scroll_area)
        
        image_ocr_layout.addWidget(image_preview_container)
        
        # OCR文本
        ocr_container = QWidget()
        ocr_layout = QVBoxLayout(ocr_container)
        ocr_layout.setContentsMargins(0, 0, 0, 0)
        ocr_layout.setSpacing(2)
        self.ocr_text_label = QLabel(STRINGS[self.parent.current_lang]['ocr_text'])
        self.ocr_text_edit = QTextEdit()
        self.ocr_text_edit.setObjectName("ocrTextEdit")
        self.ocr_text_edit.setMaximumHeight(180)
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

    def take_fullscreen(self):
        """截取全屏"""
        self.parent.showMinimized()
        
        # 给窗口最小化一点时间
        QTimer.singleShot(300, lambda: take_fullscreen_screenshot(self))

    def upload_image(self):
        """上传图像"""
        upload_image(self)

    def get_prefix_text(self):
        """获取前缀文本"""
        return self.prefix_text.toPlainText()
        
    def get_suffix_text(self):
        """获取后缀文本"""
        return self.suffix_text.toPlainText()
    
    def get_ocr_text(self):
        """获取OCR文本"""
        return self.ocr_text_edit.toPlainText()
        
    def get_image_paths(self):
        """获取所有图像路径"""
        return self.image_paths
        
    def update_texts(self):
        """更新界面上的文本为当前语言"""
        self.prefix_label.setText(STRINGS[self.parent.current_lang]['custom_prefix'])
        self.suffix_label.setText(STRINGS[self.parent.current_lang]['custom_suffix'])
        self.ocr_button.setText(STRINGS[self.parent.current_lang]['ocr_screenshot'])
        self.ocr_text_label.setText(STRINGS[self.parent.current_lang]['ocr_text'])
        self.image_upload_button.setText(STRINGS[self.parent.current_lang]['image_upload'])
        self.screenshot_button.setText(STRINGS[self.parent.current_lang]['screenshot_capture'])
        self.fullscreen_button.setText(STRINGS[self.parent.current_lang]['fullscreen_capture'])
        self.clear_image_button.setText(STRINGS[self.parent.current_lang]['clear_all_images'])
        self.image_preview_label.setText(STRINGS[self.parent.current_lang]['image_preview'])
    
    def apply_theme(self, theme):
        """应用主题样式"""
        font_family = src.config.config.UI_FONT_FAMILY
        font_size = src.config.config.UI_FONT_SIZE_NORMAL
        border_radius = src.config.config.UI_BORDER_RADIUS
        padding = src.config.config.UI_PADDING_SMALL
        
        self.setStyleSheet(f"""
            QWidget {{
                font-family: {font_family};
            }}
            QLabel {{
                font-size: {font_size};
                color: {theme['text']};
            }}
            QTextEdit {{
                font-size: {font_size};
                padding: {padding};
                border: 1px solid {theme['input_border']};
                border-radius: {border_radius};
                background-color: {theme['input_bg']};
                color: {theme['text']};
            }}
            QPushButton {{
                background-color: {theme['button_bg']};
                color: {theme['button_text']};
                padding: {padding};
                border-radius: {border_radius};
                font-size: {font_size};
            }}
            QPushButton:hover {{
                background-color: {theme['button_hover']};
            }}
            #clearButton {{
                background-color: {theme['button_danger_bg']};
            }}
            #clearButton:hover {{
                background-color: {theme['button_danger_hover']};
            }}
            QScrollArea {{
                border: 1px solid {theme['input_border']};
                border-radius: {border_radius};
                background-color: {theme['input_bg']};
            }}
            #imagesContainer {{ /* 为图像容器设置背景色 */
                background-color: {theme['input_bg']};
            }}
        """)