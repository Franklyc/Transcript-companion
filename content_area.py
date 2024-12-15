from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QComboBox, QTextEdit, QFileDialog)
from PyQt6.QtCore import Qt
import config
from lang import STRINGS
import utils
import api
import prefix

class ContentArea(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def create_labeled_layout(self, label_text, widget):
        """Create a horizontal layout with a label and widget"""
        layout = QHBoxLayout()
        label = QLabel(label_text)
        layout.addWidget(label)
        layout.addWidget(widget)
        return layout, label

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Folder selection
        self.folder_edit = QLineEdit(config.DEFAULT_FOLDER_PATH)
        self.folder_edit.setReadOnly(True)
        self.folder_button = QPushButton(STRINGS[self.parent.current_lang]['select_folder'])
        folder_layout, self.folder_label = self.create_labeled_layout(
            STRINGS[self.parent.current_lang]['current_folder'], 
            self.folder_edit
        )
        folder_layout.addWidget(self.folder_button)
        layout.addLayout(folder_layout)

        # Provider selection
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(config.PROVIDERS)
        self.provider_combo.setCurrentText(config.DEFAULT_PROVIDER)
        provider_layout, self.provider_label = self.create_labeled_layout(
            STRINGS[self.parent.current_lang].get('select_provider', 'Select Provider:'),
            self.provider_combo
        )
        layout.addLayout(provider_layout)

        # Connect provider change event
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)

        # Model selection
        self.model_combo = QComboBox()
        self.update_model_list(include_local=False)
        model_layout, self.model_label = self.create_labeled_layout(
            STRINGS[self.parent.current_lang]['select_model'],
            self.model_combo
        )
        layout.addLayout(model_layout)

        # Temperature
        self.temp_edit = QLineEdit(config.DEFAULT_TEMPERATURE)
        temp_layout, self.temp_label = self.create_labeled_layout(
            STRINGS[self.parent.current_lang]['set_temperature'],
            self.temp_edit
        )
        layout.addLayout(temp_layout)

        # Custom prefix/suffix
        self.prefix_label = QLabel(STRINGS[self.parent.current_lang]['custom_prefix'])
        self.prefix_text = QTextEdit()
        self.prefix_text.setMaximumHeight(70)
        layout.addWidget(self.prefix_label)
        layout.addWidget(self.prefix_text)

        self.suffix_label = QLabel(STRINGS[self.parent.current_lang]['custom_suffix'])
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
        self.copy_button = QPushButton(STRINGS[self.parent.current_lang]['copy_and_get_answer'])
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
        theme = config.THEMES[self.parent.current_theme]
        self.setStyleSheet(f"""
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
        """)

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
                self.status_label.setText(f"{STRINGS[self.parent.current_lang]['copied_success']}\n{STRINGS[self.parent.current_lang]['file_path']}{latest_file}")
                self.status_label.setStyleSheet("color: green")
                
                self.copy_button.setEnabled(False)
                api.fetch_model_response(combined_content, self.output_text, self.model_combo.currentText(), self.temp_edit.text())
                self.copy_button.setEnabled(True)
                
            except Exception as e:
                self.status_label.setText(f"{STRINGS[self.parent.current_lang]['read_file_error']}{e}")
                self.status_label.setStyleSheet("color: red")
                self.copy_button.setEnabled(True)
        else:
            self.status_label.setText(STRINGS[self.parent.current_lang]['no_files_available'])
            self.status_label.setStyleSheet("color: red")

    def update_texts(self):
        self.folder_label.setText(STRINGS[self.parent.current_lang]['current_folder'])
        self.folder_button.setText(STRINGS[self.parent.current_lang]['select_folder'])
        self.provider_label.setText(STRINGS[self.parent.current_lang]['select_provider'])
        self.model_label.setText(STRINGS[self.parent.current_lang]['select_model'])
        self.temp_label.setText(STRINGS[self.parent.current_lang]['set_temperature'])
        self.prefix_label.setText(STRINGS[self.parent.current_lang]['custom_prefix'])
        self.suffix_label.setText(STRINGS[self.parent.current_lang]['custom_suffix'])
        self.copy_button.setText(STRINGS[self.parent.current_lang]['copy_and_get_answer'])
