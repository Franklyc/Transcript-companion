from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor
from src.gui.lang import STRINGS
import src.config.config

class Sidebar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("sidebar")
        self.pin_button = None
        self.lang_button = None
        self.theme_button = None
        self.init_ui()
        # 显式设置背景填充属性
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(True)

    def create_sidebar_button(self, text, object_name, size=(40, 40), callback=None):
        """Create a sidebar button with common properties"""
        button = QPushButton(text)
        button.setFixedSize(*size)
        button.setObjectName(object_name)
        if callback:
            button.clicked.connect(callback)
        return button

    def init_ui(self):
        self.setFixedWidth(60)  # 稍微增大宽度以提高可用性
        
        sidebar_layout = QVBoxLayout(self)
        sidebar_layout.setContentsMargins(5, 10, 5, 10)  # 增加垂直方向边距
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.setSpacing(12)  # 增加按钮间距

        # Sidebar buttons
        sidebar_buttons = [
            ("📌", "pinButton", self.parent.toggle_stay_on_top, "固定窗口"),
            ("🀄" if self.parent.current_lang == 'zh' else "🔤", "langButton", self.parent.toggle_language, "切换语言"),
            ("🌙" if self.parent.current_theme == "light" else "☀️", "themeButton", self.parent.toggle_theme, "切换主题"),
            ("❓", "helpButton", self.parent.show_help, "帮助"),
            ("⚙️", "settingsButton", self.parent.show_settings, "设置"),
            ("🗑️", "clearButton", self.parent.clear_content, "清除内容"),
            ("🔄", "refreshButton", lambda: self.parent.update_model_list(True), "刷新模型列表"),
        ]

        for text, obj_name, callback, tooltip in sidebar_buttons:
            button = QPushButton(text)
            button.setObjectName(obj_name)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setFixedSize(42, 42)  # 设置统一的按钮大小
            button.clicked.connect(callback)
            button.setToolTip(tooltip)
            
            # 保存一些重要按钮的引用
            if obj_name == "pinButton":
                self.pin_button = button
            elif obj_name == "langButton":
                self.lang_button = button
            elif obj_name == "themeButton":
                self.theme_button = button
            
            sidebar_layout.addWidget(button)
            
        sidebar_layout.addStretch()

    def apply_theme(self):
        theme = src.config.config.THEMES[self.parent.current_theme]
        font_size_normal = src.config.config.UI_FONT_SIZE_NORMAL
        font_size_large = src.config.config.UI_FONT_SIZE_LARGE
        border_radius = src.config.config.UI_BORDER_RADIUS
        padding = src.config.config.UI_PADDING_SMALL
        shadow = src.config.config.UI_SHADOW
        
        # 设置背景色和边框
        self.setStyleSheet(f"""
            QWidget#sidebar {{
                background-color: {theme['sidebar_bg']};
                border-top-left-radius: {border_radius};
                border-bottom-left-radius: {border_radius};
                border-right: none;
            }}
            #pinButton, #langButton, #themeButton, #helpButton, #settingsButton, #clearButton, #refreshButton {{
                background-color: transparent;
                border: none;
                color: {theme['text']};
                font-size: 16pt;
                padding: {padding};
                margin: 2px;
                border-radius: 12px;
            }}
            #pinButton:hover, #langButton:hover, #themeButton:hover, #helpButton:hover, #settingsButton:hover {{
                background-color: rgba(255, 255, 255, 0.15);
                border-radius: 12px;
            }}
            #clearButton:hover {{
                background-color: rgba(232, 17, 35, 0.2);
                border-radius: 12px;
            }}
            #refreshButton:hover {{
                background-color: rgba(59, 130, 246, 0.2);
                border-radius: 12px;
            }}
        """)
