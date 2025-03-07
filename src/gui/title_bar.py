from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt
from src.gui.lang import STRINGS
import src.config.config

class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        
        # 启用背景样式
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def create_title_button(self, text, callback):
        """Create a title bar button with common properties"""
        button = QPushButton(text)
        button.setFixedSize(30, 30)
        button.setObjectName("titleButton")
        button.clicked.connect(callback)
        return button

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(5)
        
        self.title_label = QLabel(STRINGS[self.parent.current_lang]['window_title'])
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 添加应用图标
        self.icon_label = QLabel("🎙️")
        self.icon_label.setObjectName("iconLabel")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 最小化按钮
        self.min_button = QPushButton("🗕")
        self.min_button.setObjectName("minButton")
        self.min_button.setFlat(True)  # 设置为扁平按钮，更接近现代UI
        self.min_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.min_button.clicked.connect(self.parent.showMinimized)
        
        # 关闭按钮
        self.close_button = QPushButton("✖")
        self.close_button.setObjectName("closeButton")
        self.close_button.setFlat(True)  # 设置为扁平按钮，更接近现代UI
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button.clicked.connect(self.parent.close)
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.min_button)
        layout.addWidget(self.close_button)

    def update_title(self):
        """更新标题文本"""
        self.title_label.setText(STRINGS[self.parent.current_lang]['window_title'])

    def apply_theme(self):
        theme = src.config.config.THEMES[self.parent.current_theme]
        font_family = src.config.config.UI_FONT_FAMILY
        font_size_normal = src.config.config.UI_FONT_SIZE_NORMAL
        font_size_large = src.config.config.UI_FONT_SIZE_LARGE
        border_radius = src.config.config.UI_BORDER_RADIUS
        
        self.setStyleSheet(f"""
            QWidget {{
                font-family: {font_family};
                background-color: transparent;
                border-top-right-radius: {border_radius};
            }}
            #titleLabel {{
                color: {theme['text']};
                font-size: {font_size_large};
                font-weight: bold;
                margin-left: 2px;
            }}
            #iconLabel {{
                color: {theme['text']};
                font-size: {font_size_large};
            }}
            #minButton, #closeButton {{
                background-color: transparent;
                border: none;
                color: {theme['text']};
                font-size: {font_size_normal};
                padding: 4px 8px;
                border-radius: 4px;
            }}
            #closeButton:hover {{
                background-color: {theme['button_danger_bg']};
                color: white;
            }}
            #minButton:hover {{
                background-color: {theme['button_hover']};
                color: white;
            }}
        """)
