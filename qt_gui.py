from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLabel, QComboBox, QLineEdit, QTextEdit, QFileDialog,
                           QRadioButton, QButtonGroup, QScrollBar, QMessageBox, QDialog, QCheckBox)
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

    def create_sidebar_button(self, text, object_name, size=(40, 40), callback=None):
        """Create a sidebar button with common properties"""
        button = QPushButton(text)
        button.setFixedSize(*size)
        button.setObjectName(object_name)
        if callback:
            button.clicked.connect(callback)
        return button

    def create_title_button(self, text, callback):
        """Create a title bar button with common properties"""
        button = QPushButton(text)
        button.setFixedSize(30, 30)
        button.setObjectName("titleButton")
        button.clicked.connect(callback)
        return button

    def create_labeled_layout(self, label_text, widget):
        """Create a horizontal layout with a label and widget"""
        layout = QHBoxLayout()
        label = QLabel(label_text)
        layout.addWidget(label)
        layout.addWidget(widget)
        return layout, label

    def init_ui(self):
        self.setWindowTitle(STRINGS[self.current_lang]['window_title'])
        self.setFixedSize(650, 700)  # Increased width to accommodate sidebar

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        horizontal_layout = QHBoxLayout(central_widget)
        horizontal_layout.setContentsMargins(0, 0, 0, 0)
        horizontal_layout.setSpacing(0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(50)
        sidebar.setObjectName("sidebar")  # 添加这行来设置ObjectName
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(5, 5, 5, 5)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Sidebar buttons
        sidebar_buttons = [
            ("🀄" if self.current_lang == 'zh' else "🔤", "langButton", self.toggle_language),
            ("🌙" if self.current_theme == "light" else "☀️", "themeButton", self.toggle_theme),
            ("❓", "sidebarButton", self.show_help),
            ("⚙️", "sidebarButton", self.show_settings),
            ("🗑️", "sidebarButton", self.clear_content),
            ("🔄", "sidebarButton", lambda: self.update_model_list(True)),
        ]

        for text, obj_name, callback in sidebar_buttons:
            button = self.create_sidebar_button(text, obj_name, callback=callback)
            sidebar_layout.addWidget(button)
            if obj_name == "langButton":
                self.lang_button = button
            elif obj_name == "themeButton":
                self.theme_button = button

        sidebar_layout.addStretch()
        horizontal_layout.addWidget(sidebar)

        # Main content area
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Title bar
        title_bar = QWidget()
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 5, 10, 5)

        # 标题文本
        self.title_label = QLabel(STRINGS[self.current_lang]['window_title'])
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()

        # Title bar buttons
        min_button = self.create_title_button("－", self.showMinimized)
        close_button = self.create_title_button("✕", self.close)
        title_layout.addWidget(min_button)
        title_layout.addWidget(close_button)

        main_layout.addWidget(title_bar)

        # 内容区域
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        main_layout.addWidget(content_widget)

        horizontal_layout.addWidget(main_container)

        # Folder selection
        self.folder_edit = QLineEdit(config.DEFAULT_FOLDER_PATH)
        self.folder_edit.setReadOnly(True)
        self.folder_button = QPushButton(STRINGS[self.current_lang]['select_folder'])
        folder_layout, self.folder_label = self.create_labeled_layout(
            STRINGS[self.current_lang]['current_folder'], 
            self.folder_edit
        )
        folder_layout.addWidget(self.folder_button)
        layout.addLayout(folder_layout)

        # Provider selection
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(config.PROVIDERS)
        self.provider_combo.setCurrentText(config.DEFAULT_PROVIDER)
        provider_layout, self.provider_label = self.create_labeled_layout(
            STRINGS[self.current_lang].get('select_provider', 'Select Provider:'),
            self.provider_combo
        )
        layout.addLayout(provider_layout)

        # Connect provider change event
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)

        # Model selection
        self.model_combo = QComboBox()
        self.update_model_list(include_local=False)
        model_layout, self.model_label = self.create_labeled_layout(
            STRINGS[self.current_lang]['select_model'],
            self.model_combo
        )
        layout.addLayout(model_layout)

        # Temperature
        self.temp_edit = QLineEdit(config.DEFAULT_TEMPERATURE)
        temp_layout, self.temp_label = self.create_labeled_layout(
            STRINGS[self.current_lang]['set_temperature'],
            self.temp_edit
        )
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

    def update_model_list(self, include_local=False):
        current_model = self.model_combo.currentText()
        config.refresh_available_models(include_local)
        self.model_combo.clear()
        
        # Filter models by selected provider
        provider = self.provider_combo.currentText()
        filtered_models = config.filter_models_by_provider(provider)
        self.model_combo.addItems(filtered_models)
        
        # Try to restore previous selection
        index = self.model_combo.findText(current_model)
        if index >= 0:
            self.model_combo.setCurrentIndex(index)
        elif self.model_combo.count() > 0:
            self.model_combo.setCurrentIndex(0)

    def on_provider_changed(self, provider):
        """Handle provider selection change"""
        self.update_model_list(self.provider_combo.currentText() in ["LMstudio", "Kobold", "Ollama"])

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
            #titleButton {{
                background-color: transparent;
                border: none;
                color: {theme['text']};
                font-size: 16px;
            }}
            #titleButton:hover {{
                background-color: {theme['title_button_hover']};
                color: white;
            }}
            #themeButton {{
                background-color: transparent;
                border: none;
                color: {theme['text']};
                font-size: 16px;
                padding: 4px;
            }}
            #themeButton:hover {{
                background-color: {theme['input_border']};
            }}
            QWidget#sidebar {{
                background-color: {theme['sidebar_bg']};
                border-right: 1px solid {theme['input_border']};
            }}
            QRadioButton {{
                color: {theme['text']};
                padding: 5px;
                margin: 2px;
            }}
            QRadioButton:hover {{
                background-color: {theme['input_border']};
                border-radius: 4px;
            }}
            #langButton {{
                background-color: transparent;
                border: none;
                color: {theme['text']};
                font-size: 16px;
                padding: 4px;
            }}
            #langButton:hover {{
                background-color: {theme['input_border']};
            }}
            #sidebarButton {{
                background-color: transparent;
                border: none;
                color: {theme['text']};
                font-size: 16px;
                padding: 4px;
            }}
            #sidebarButton:hover {{
                background-color: {theme['input_border']};
                border-radius: 4px;
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
        original_prefix = prefix.get_original_prefix() if config.USE_PREDEFINED_PREFIX else ""

        if latest_file:
            try:
                transcript_content = ""
                if config.USE_TRANSCRIPT_TEXT:
                    with open(latest_file, 'r', encoding='utf-8') as file:
                        transcript_content = file.read()

                combined_content = f"{original_prefix}\n{self.prefix_text.toPlainText()}\n{transcript_content}\n{self.suffix_text.toPlainText()}"
                utils.copy_to_clipboard(combined_content)
                self.status_label.setText(f"{STRINGS[self.current_lang]['copied_success']}\n{STRINGS[self.current_lang]['file_path']}{latest_file}")
                self.status_label.setStyleSheet("color: green")
                
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

    def toggle_language(self):
        self.current_lang = 'en' if self.current_lang == 'zh' else 'zh'
        self.lang_button.setText("🀄" if self.current_lang == 'zh' else "🔤")
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

    # Add new methods for the new buttons
    def show_help(self):
        help_text = STRINGS[self.current_lang]['help_text']
        QMessageBox.information(self, STRINGS[self.current_lang]['help_title'], help_text)

    def show_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def clear_content(self):
        self.output_text.clear()
        self.prefix_text.clear()
        self.suffix_text.clear()
        self.status_label.clear()

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle(STRINGS[self.parent.current_lang]['settings_title'])
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Create checkboxes
        self.prefix_checkbox = QCheckBox(STRINGS[self.parent.current_lang]['use_predefined_prefix'])
        self.prefix_checkbox.setChecked(config.USE_PREDEFINED_PREFIX)
        
        self.transcript_checkbox = QCheckBox(STRINGS[self.parent.current_lang]['use_transcript_text'])
        self.transcript_checkbox.setChecked(config.USE_TRANSCRIPT_TEXT)

        # Add checkboxes to layout
        layout.addWidget(self.prefix_checkbox)
        layout.addWidget(self.transcript_checkbox)

        self.setLayout(layout)

        # Connect signals
        self.prefix_checkbox.stateChanged.connect(self.update_settings)
        self.transcript_checkbox.stateChanged.connect(self.update_settings)

    def update_settings(self):
        config.USE_PREDEFINED_PREFIX = self.prefix_checkbox.isChecked()
        config.USE_TRANSCRIPT_TEXT = self.transcript_checkbox.isChecked()

    def apply_theme(self):
        theme = config.THEMES[self.parent.current_theme]
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme['dialog_bg']};
            }}
            QCheckBox {{
                color: {theme['text']};
            }}
        """)