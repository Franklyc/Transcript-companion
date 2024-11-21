from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLabel, QComboBox, QLineEdit, QTextEdit, QFileDialog,
                           QRadioButton, QButtonGroup, QScrollBar)
from PyQt6.QtCore import Qt, QPoint
import config
import utils
import api
from lang import STRINGS
import prefix

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(flags=Qt.WindowType.FramelessWindowHint)  # 无边框窗口
        self.old_pos = None  # 用于窗口拖动
        self.current_lang = 'zh'
        self.current_theme = config.DEFAULT_THEME
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(STRINGS[self.current_lang]['window_title'])
        self.setFixedSize(600, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 自定义标题栏
        title_bar = QWidget()
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 5, 10, 5)

        # 标题文本
        self.title_label = QLabel(STRINGS[self.current_lang]['window_title'])
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()

        # 控制按钮
        min_button = QPushButton("－")
        close_button = QPushButton("✕")
        for btn in (min_button, close_button):
            btn.setFixedSize(30, 30)
            title_layout.addWidget(btn)

        min_button.clicked.connect(self.showMinimized)
        close_button.clicked.connect(self.close)

        main_layout.addWidget(title_bar)

        # 内容区域
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        main_layout.addWidget(content_widget)

        # Language selection
        lang_layout = QHBoxLayout()
        self.lang_group = QButtonGroup(self)
        zh_radio = QRadioButton("中文")
        en_radio = QRadioButton("English")
        zh_radio.setChecked(True)
        self.lang_group.addButton(zh_radio, 1)
        self.lang_group.addButton(en_radio, 2)
        lang_layout.addWidget(zh_radio)
        lang_layout.addWidget(en_radio)
        lang_layout.addStretch()

        # Add theme toggle
        self.theme_button = QPushButton("🌙" if self.current_theme == "light" else "☀️")
        self.theme_button.setFixedSize(30, 30)
        self.theme_button.clicked.connect(self.toggle_theme)
        lang_layout.addWidget(self.theme_button)

        layout.addLayout(lang_layout)

        # Folder selection
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel(STRINGS[self.current_lang]['current_folder'])
        self.folder_edit = QLineEdit(config.DEFAULT_FOLDER_PATH)
        self.folder_edit.setReadOnly(True)
        self.folder_button = QPushButton(STRINGS[self.current_lang]['select_folder'])
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.folder_edit)
        folder_layout.addWidget(self.folder_button)
        layout.addLayout(folder_layout)

        # Model selection
        model_layout = QHBoxLayout()
        self.model_label = QLabel(STRINGS[self.current_lang]['select_model'])
        self.model_combo = QComboBox()
        self.model_combo.addItems(config.AVAILABLE_MODELS)
        model_layout.addWidget(self.model_label)
        model_layout.addWidget(self.model_combo)
        layout.addLayout(model_layout)

        # Temperature
        temp_layout = QHBoxLayout()
        self.temp_label = QLabel(STRINGS[self.current_lang]['set_temperature'])
        self.temp_edit = QLineEdit(config.DEFAULT_TEMPERATURE)
        temp_layout.addWidget(self.temp_label)
        temp_layout.addWidget(self.temp_edit)
        layout.addLayout(temp_layout)

        # Custom prefix/suffix
        self.prefix_label = QLabel(STRINGS[self.current_lang]['custom_prefix'])
        self.prefix_text = QTextEdit()
        self.prefix_text.setMaximumHeight(70)
        layout.addWidget(self.prefix_label)
        layout.addWidget(self.prefix_text)

        self.suffix_label = QLabel(STRINGS[self.current_lang]['custom_suffix'])
        self.suffix_text = QTextEdit()
        self.suffix_text.setMaximumHeight(70)
        layout.addWidget(self.suffix_label)
        layout.addWidget(self.suffix_text)

        # Status label
        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        # Output text
        self.output_text = QTextEdit()
        layout.addWidget(self.output_text)

        # Copy button
        self.copy_button = QPushButton(STRINGS[self.current_lang]['copy_and_get_answer'])
        self.copy_button.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
        """)
        layout.addWidget(self.copy_button)

        # Connect signals
        self.folder_button.clicked.connect(self.select_folder)
        self.copy_button.clicked.connect(self.copy_and_get_answer)
        self.lang_group.buttonClicked.connect(self.change_language)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #F0F0F0;
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

    def apply_theme(self):
        theme = config.THEMES[self.current_theme]
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme['window_bg']};
                border: 1px solid {theme['input_border']};
            }}
            QLabel {{
                font-size: 10pt;
                color: {theme['text']};
            }}
            QTextEdit, QLineEdit, QComboBox {{
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
            QRadioButton {{
                color: {theme['text']};
            }}
            #title_bar {{
                background-color: {theme['window_bg']};
            }}
            #title_bar QPushButton {{
                background-color: transparent;
                border: none;
                color: {theme['text']};
                font-size: 16px;
            }}
            #title_bar QPushButton:hover {{
                background-color: {theme['button_hover']};
            }}
        """)

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.theme_button.setText("🌙" if self.current_theme == "light" else "☀️")
        self.apply_theme()

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self)
        if folder_path:
            self.folder_edit.setText(folder_path)

    def copy_and_get_answer(self):
        directory = self.folder_edit.text()
        latest_file = utils.get_latest_file(directory)
        original_prefix = prefix.get_original_prefix()

        if latest_file:
            try:
                with open(latest_file, 'r', encoding='utf-8') as file:
                    content = file.read()
                combined_content = f"{original_prefix}\n{self.prefix_text.toPlainText()}\n{content}\n{self.suffix_text.toPlainText()}"
                utils.copy_to_clipboard(combined_content)
                self.status_label.setText(f"{STRINGS[self.current_lang]['copied_success']}\n{STRINGS[self.current_lang]['file_path']}{latest_file}")
                self.status_label.setStyleSheet("color: green")
                
                # Disable copy button during API call
                self.copy_button.setEnabled(False)
                api.fetch_model_response(combined_content, self.output_text, self.model_combo.currentText(), self.temp_edit.text())
                self.copy_button.setEnabled(True)
                
            except Exception as e:
                self.status_label.setText(f"{STRINGS[self.current_lang]['read_file_error']}{e}")
                self.status_label.setStyleSheet("color: red")
                self.copy_button.setEnabled(True)
        else:
            self.status_label.setText(STRINGS[self.current_lang]['no_files_available'])
            self.status_label.setStyleSheet("color: red")

    def change_language(self, button):
        self.current_lang = 'en' if button.text() == "English" else 'zh'
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
        self.title_label.setText(STRINGS[self.current_lang]['window_title'])
        self.setWindowTitle(STRINGS[self.current_lang]['window_title'])
        self.folder_label.setText(STRINGS[self.current_lang]['current_folder'])
        self.folder_button.setText(STRINGS[self.current_lang]['select_folder'])
        self.model_label.setText(STRINGS[self.current_lang]['select_model'])
        self.temp_label.setText(STRINGS[self.current_lang]['set_temperature'])
        self.prefix_label.setText(STRINGS[self.current_lang]['custom_prefix'])
        self.suffix_label.setText(STRINGS[self.current_lang]['custom_suffix'])
        self.copy_button.setText(STRINGS[self.current_lang]['copy_and_get_answer'])