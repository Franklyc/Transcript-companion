from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLabel, QComboBox, QLineEdit, QTextEdit, QFileDialog,
                           QRadioButton, QButtonGroup, QScrollBar, QMessageBox, QDialog, QCheckBox)
from PyQt6.QtCore import Qt, QPoint, QEvent
import src.config.config
import src.gui.utils
import src.api.api
from src.gui.lang import STRINGS
import src.gui.prefix
from src.gui.title_bar import TitleBar
from src.gui.sidebar import Sidebar
from src.gui.content_area import ContentArea
from src.gui.settings_dialog import SettingsDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(flags=Qt.WindowType.FramelessWindowHint)  # 无边框窗口
        self.old_pos = None  # 用于窗口拖动
        self.current_lang = 'zh'
        self.current_theme = src.config.config.DEFAULT_THEME
        
        # 启用窗口透明度
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(STRINGS[self.current_lang]['window_title'])
        self.setFixedSize(550, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        horizontal_layout = QHBoxLayout(central_widget)
        horizontal_layout.setContentsMargins(10, 10, 10, 10)  # 增加边距，创造悬浮效果
        horizontal_layout.setSpacing(0)

        # 创建主窗口容器
        main_container_wrapper = QWidget()
        main_container_wrapper.setObjectName("mainContainerWrapper")
        wrapper_layout = QVBoxLayout(main_container_wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar(self)
        horizontal_layout.addWidget(self.sidebar)

        # Main content area
        self.main_container = QWidget()
        self.main_container.setObjectName("mainContainer")
        main_layout = QVBoxLayout(self.main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Title bar
        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)

        # Content area
        self.content_area = ContentArea(self)
        main_layout.addWidget(self.content_area)

        # 将主容器添加到包装器中
        wrapper_layout.addWidget(self.main_container)
        horizontal_layout.addWidget(main_container_wrapper)

        self.apply_theme()

    def apply_theme(self):
        theme = src.config.config.THEMES[self.current_theme]
        font_family = src.config.config.UI_FONT_FAMILY
        border_radius = src.config.config.UI_BORDER_RADIUS
        shadow = src.config.config.UI_SHADOW
        
        # 应用主题到各个组件
        self.title_bar.apply_theme()
        self.sidebar.apply_theme()
        self.content_area.apply_theme()
        
        # 设置主窗口样式
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: transparent;
                font-family: {font_family};
            }}
            
            #mainContainerWrapper {{
                background-color: {theme['window_bg']};
                border-radius: {border_radius};
                border: {src.config.config.UI_BORDER_WIDTH} solid {theme['glass_border']};
            }}
            
            #mainContainer {{
                background-color: transparent;
                padding-left: 1px;
            }}
            
            QComboBox QAbstractItemView {{
                color: {theme['dropdown_text']};
                background-color: {theme['dropdown_bg']};
                selection-background-color: {theme['button_bg']};
                selection-color: {theme['button_text']};
                border: 1px solid {theme['glass_border']};
                border-radius: {border_radius};
            }}
            
            QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 8px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {theme['input_border']};
                min-height: 30px;
                border-radius: 4px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {theme['button_bg']};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar:horizontal {{
                border: none;
                background: transparent;
                height: 8px;
                margin: 0px;
            }}
            
            QScrollBar::handle:horizontal {{
                background: {theme['input_border']};
                min-width: 30px;
                border-radius: 4px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background: {theme['button_bg']};
            }}
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            
            QToolTip {{
                color: {theme['text']};
                background-color: {theme['input_bg']};
                border: 1px solid {theme['input_border']};
                border-radius: {border_radius};
                padding: 4px;
                font-family: {font_family};
            }}
        """)

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.sidebar.theme_button.setText("🌙" if self.current_theme == "light" else "☀️")
        self.apply_theme()

    def select_folder(self):
        self.content_area.select_folder()

    def copy_and_get_answer(self):
        self.content_area.copy_and_get_answer()

    def toggle_language(self):
        self.current_lang = 'en' if self.current_lang == 'zh' else 'zh'
        self.sidebar.lang_button.setText("🀄" if self.current_lang == 'zh' else "🔤")
        self.update_texts()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = None

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def update_texts(self):
        self.title_bar.update_title()
        self.content_area.update_texts()

    def show_help(self):
        help_text = STRINGS[self.current_lang]['help_text']
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(STRINGS[self.current_lang]['help_title'])
        msg_box.setText(help_text)
        msg_box.setIcon(QMessageBox.Icon.Information)
    
        # Apply theme to message box
        theme = src.config.config.THEMES[self.current_theme]
        font_family = src.config.config.UI_FONT_FAMILY
        font_size = src.config.config.UI_FONT_SIZE_NORMAL
        border_radius = src.config.config.UI_BORDER_RADIUS
        padding = src.config.config.UI_PADDING_NORMAL
        
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {theme['dialog_bg']};
                font-family: {font_family};
                border: {src.config.config.UI_BORDER_WIDTH} solid {theme['glass_border']};
                border-radius: {border_radius};
            }}
            QLabel {{
                color: {theme['text']};
                background-color: transparent;
                font-size: {font_size};
            }}
            QPushButton {{
                background-color: {theme['button_bg']};
                color: {theme['button_text']};
                padding: 6px 14px;
                border-radius: {border_radius};
                min-width: 80px;
                font-family: {font_family};
            }}
            QPushButton:hover {{
                background-color: {theme['button_hover']};
            }}
        """)
    
        msg_box.exec()

    def show_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def clear_content(self):
        # 清除输出区域
        self.content_area.output_area.clear_output()
        self.content_area.output_area.set_status("")
        
        # 清除输入区域文本
        self.content_area.input_tab.prefix_text.clear()
        self.content_area.input_tab.suffix_text.clear()
        self.content_area.input_tab.ocr_text_edit.clear()
        
        # 使用新的清理图像功能代替旧的image_display.clear()
        from src.gui.image_utils import clear_image
        clear_image(self.content_area.input_tab)

    def update_model_list(self, include_local=False):
        self.content_area.update_model_list(include_local)
    
    def toggle_stay_on_top(self):
        """切换窗口置顶状态"""
        flags = self.windowFlags()
        if flags & Qt.WindowType.WindowStaysOnTopHint:
            # 取消置顶
            self.setWindowFlags(flags & ~Qt.WindowType.WindowStaysOnTopHint)
            self.sidebar.pin_button.setText("📌")
            self.sidebar.pin_button.setToolTip("Pin window (keep on top)")
        else:
            # 设置置顶
            self.setWindowFlags(flags | Qt.WindowType.WindowStaysOnTopHint)
            self.sidebar.pin_button.setText("📍")
            self.sidebar.pin_button.setToolTip("Unpin window")
        
        # 重新显示窗口以应用更改
        self.show()