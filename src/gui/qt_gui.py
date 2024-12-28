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
        self.installEventFilter(self)  # 安装全局事件过滤器

    def init_ui(self):
        self.setWindowTitle(STRINGS[self.current_lang]['window_title'])
        self.setFixedSize(650, 700)  # Increased width to accommodate sidebar

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
        main_layout = QVBoxLayout(self.main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Title bar
        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)

        # Content area
        self.content_area = ContentArea(self)
        main_layout.addWidget(self.content_area)

        horizontal_layout.addWidget(self.main_container)

        self.setStyleSheet("""
            QMainWindow {
                
            }
            QLabel {
                font-size: 10pt;
            }
            QTextEdit, QLineEdit, QComboBox {
                font-size: 10pt;
                padding: 4px;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
            }
        """)

        self.apply_theme()

    def eventFilter(self, obj, event):
        """全局事件过滤器，用于捕获鼠标在屏幕范围内的操作"""
        if self.content_area.ocr_enabled:
            if event.type() == QEvent.Type.MouseButtonPress:
                self.content_area.mousePressEvent(event)
            elif event.type() == QEvent.Type.MouseMove:
                self.content_area.mouseMoveEvent(event)
            elif event.type() == QEvent.Type.MouseButtonRelease:
                self.content_area.mouseReleaseEvent(event)
        return super().eventFilter(obj, event)

    def apply_theme(self):
        theme = src.config.config.THEMES[self.current_theme]
        # 设置主窗口背景色
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme['window_bg']};
                border: 1px solid {theme['input_border']};
            }}
            QComboBox QAbstractItemView {{
                color: {theme['dropdown_text']};
                background-color: {theme['input_bg']};
            }}
        """)
        self.main_container.setStyleSheet(f"""
            QWidget {{
                background-color: {theme['window_bg']};
            }}
        """)
        # 应用主题到各个组件
        self.title_bar.apply_theme()
        self.sidebar.apply_theme()
        self.content_area.apply_theme()

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
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {theme['dialog_bg']};
                color: {theme['text']};
            }}
            QLabel {{
                color: {theme['text']};
                background-color: {theme['dialog_bg']};
            }}
            QPushButton {{
                background-color: {theme['button_bg']};
                color: {theme['button_text']};
                padding: 6px 14px;
                border-radius: 4px;
                min-width: 80px;
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
        self.content_area.output_text.clear()
        self.content_area.prefix_text.clear()
        self.content_area.suffix_text.clear()
        self.content_area.status_label.clear()

    def update_model_list(self, include_local=False):
        self.content_area.update_model_list(include_local)