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
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(STRINGS[self.current_lang]['window_title'])
        self.setFixedSize(650, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        horizontal_layout = QHBoxLayout(central_widget)
        horizontal_layout.setContentsMargins(0, 0, 0, 0)
        horizontal_layout.setSpacing(0)

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

        horizontal_layout.addWidget(self.main_container)

        self.apply_theme()

    def apply_theme(self):
        theme = src.config.config.THEMES[self.current_theme]
        font_family = src.config.config.UI_FONT_FAMILY
        border_radius = src.config.config.UI_BORDER_RADIUS
        
        # 应用主题到各个组件
        self.title_bar.apply_theme()
        self.sidebar.apply_theme()
        self.content_area.apply_theme()
        
        # 设置主窗口样式
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme['window_bg']};
                border: 1px solid {theme['input_border']};
                font-family: {font_family};
            }}
            
            #mainContainer {{
                background-color: {theme['window_bg']};
            }}
            
            QComboBox QAbstractItemView {{
                color: {theme['dropdown_text']};
                background-color: {theme['input_bg']};
                selection-background-color: {theme['button_bg']};
                selection-color: {theme['button_text']};
            }}
            
            QScrollBar:vertical {{
                border: none;
                background: {theme['window_bg']};
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
                background: {theme['window_bg']};
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
                padding: 2px;
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
            }}
            QLabel {{
                color: {theme['text']};
                background-color: {theme['dialog_bg']};
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
        self.content_area.input_tab.image_display.clear()
        self.content_area.input_tab.current_image_path = None

    def update_model_list(self, include_local=False):
        self.content_area.update_model_list(include_local)