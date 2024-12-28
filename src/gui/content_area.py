from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                           QPushButton, QComboBox, QTextEdit, QFileDialog, QMessageBox)
from PyQt6.QtGui import QScreen, QPixmap, QPainter, QColor, QGuiApplication
from PyQt6.QtCore import Qt, QRect, QPoint
import src.config.config
from src.gui.lang import STRINGS
import src.gui.utils
import src.api.api
import src.gui.prefix
import os
import datetime
import textract
from PIL import Image

class ContentArea(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.ocr_enabled = False
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.selection_overlay = None
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
        self.folder_edit = QLineEdit(src.config.config.DEFAULT_FOLDER_PATH)
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
        self.provider_combo.addItems(src.config.config.PROVIDERS)
        self.provider_combo.setCurrentText(src.config.config.DEFAULT_PROVIDER)
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
        self.temp_edit = QLineEdit(src.config.config.DEFAULT_TEMPERATURE)
        temp_layout, self.temp_label = self.create_labeled_layout(
            STRINGS[self.parent.current_lang]['set_temperature'],
            self.temp_edit
        )
        layout.addLayout(temp_layout)

        # Custom prefix/suffix
        self.prefix_label = QLabel(STRINGS[self.parent.current_lang]['custom_prefix'])
        self.prefix_text = QTextEdit()
        self.prefix_text.setMaximumHeight(30)
        layout.addWidget(self.prefix_label)
        layout.addWidget(self.prefix_text)

        self.suffix_label = QLabel(STRINGS[self.parent.current_lang]['custom_suffix'])
        self.suffix_text = QTextEdit()
        self.suffix_text.setMaximumHeight(30)
        layout.addWidget(self.suffix_label)
        layout.addWidget(self.suffix_text)

        # OCR Functionality
        self.ocr_button = QPushButton(STRINGS[self.parent.current_lang]['ocr_screenshot'])
        self.ocr_button.clicked.connect(self.enable_ocr)
        layout.addWidget(self.ocr_button)

        self.ocr_text_label = QLabel(STRINGS[self.parent.current_lang]['ocr_text'])
        layout.addWidget(self.ocr_text_label)
        self.ocr_text_edit = QTextEdit()
        self.ocr_text_edit.setMaximumHeight(100)
        layout.addWidget(self.ocr_text_edit)

        # Status label
        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        # Output text
        self.output_text = QTextEdit()
        layout.addWidget(self.output_text)

        # Buttons layout
        buttons_layout = QHBoxLayout()

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
        buttons_layout.addWidget(self.copy_button)

        # Export button
        self.export_button = QPushButton(STRINGS[self.parent.current_lang]['export_conversation'])
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #367C39;
            }
        """)
        buttons_layout.addWidget(self.export_button)
        layout.addLayout(buttons_layout)

        # Connect signals
        self.folder_button.clicked.connect(self.select_folder)
        self.copy_button.clicked.connect(self.copy_and_get_answer)
        self.export_button.clicked.connect(self.export_conversation)

    def update_model_list(self, include_local=False):
        current_model = self.model_combo.currentText()
        src.config.config.refresh_available_models(include_local)
        self.model_combo.clear()

        # Filter models by selected provider
        provider = self.provider_combo.currentText()
        filtered_models = src.config.config.filter_models_by_provider(provider)
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
        theme = src.config.config.THEMES[self.parent.current_theme]
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

    def enable_ocr(self):
        self.ocr_enabled = True
        self.parent.setMouseTracking(True)
        QApplication.instance().setOverrideCursor(Qt.CursorShape.CrossCursor)
        self.status_label.setText(STRINGS[self.parent.current_lang]['ocr_instructions'])
        self.status_label.setStyleSheet("color: blue")

    def mousePressEvent(self, event):
        if self.ocr_enabled and event.button() == Qt.MouseButton.RightButton:
            self.start_point = event.pos()
            self.end_point = self.start_point
            self.update_selection_overlay()

    def mouseMoveEvent(self, event):
        if self.ocr_enabled and event.buttons() & Qt.MouseButton.RightButton:
            self.end_point = event.pos()
            self.update_selection_overlay()

    def mouseReleaseEvent(self, event):
        if self.ocr_enabled and event.button() == Qt.MouseButton.RightButton:
            self.ocr_enabled = False
            self.parent.setMouseTracking(False)
            QApplication.instance().restoreOverrideCursor()
            self.capture_and_ocr()

    def leaveEvent(self, event):
        # No need to handle mouse position here
        pass

    def update_selection_overlay(self):
        if not self.selection_overlay:
            self.selection_overlay = SelectionOverlay(self)
        rect = QRect(self.start_point, self.end_point).normalized()
        self.selection_overlay.setGeometry(self.mapToGlobal(rect.topLeft()).x(),
                                            self.mapToGlobal(rect.topLeft()).y(),
                                            rect.width(), rect.height())
        self.selection_overlay.show()
        self.selection_overlay.raise_()

    def capture_and_ocr(self):
        if self.selection_overlay:
            geometry = self.selection_overlay.geometry()
            self.selection_overlay.hide()
            self.selection_overlay.destroy()
            self.selection_overlay = None

            x, y, w, h = geometry.x(), geometry.y(), geometry.width(), geometry.height()
            screenshot = QScreen.grabWindow(QGuiApplication.primaryScreen(), 0, x, y, w, h)
            image = screenshot.toImage()
            image_path = os.path.join(os.getcwd(), "temp_screenshot.png")
            image.save(image_path)

            try:
                text = textract.process(image_path).decode('utf-8')
                self.ocr_text_edit.setText(text)
                self.status_label.setText(STRINGS[self.parent.current_lang]['ocr_success'])
                self.status_label.setStyleSheet("color: green")
            except Exception as e:
                self.status_label.setText(f"{STRINGS[self.parent.current_lang]['ocr_error']}: {e}")
                self.status_label.setStyleSheet("color: red")
            finally:
                if os.path.exists(image_path):
                    os.remove(image_path)
        else:
            self.status_label.setText(STRINGS[self.parent.current_lang]['ocr_selection_canceled'])
            self.status_label.setStyleSheet("color: orange")

    def copy_and_get_answer(self):
        directory = self.folder_edit.text()
        latest_file = src.gui.utils.get_latest_file(directory)
        original_prefix = src.gui.prefix.get_original_prefix() if src.config.config.USE_PREDEFINED_PREFIX else ""
        ocr_text = self.ocr_text_edit.toPlainText()

        if latest_file:
            try:
                transcript_content = ""
                if src.config.config.USE_TRANSCRIPT_TEXT:
                    with open(latest_file, 'r', encoding='utf-8') as file:
                        transcript_content = file.read()

                combined_content = f"{original_prefix}\n{self.prefix_text.toPlainText()}\n{transcript_content}\n{self.suffix_text.toPlainText()}\n{ocr_text}"
                src.gui.utils.copy_to_clipboard(combined_content)
                self.status_label.setText(f"{STRINGS[self.parent.current_lang]['copied_success']}\n{STRINGS[self.parent.current_lang]['file_path']}{latest_file}")
                self.status_label.setStyleSheet("color: green")

                self.copy_button.setEnabled(False)
                src.api.api.fetch_model_response(combined_content, self.output_text, self.model_combo.currentText(), self.temp_edit.text())
                self.copy_button.setEnabled(True)

            except Exception as e:
                self.status_label.setText(f"{STRINGS[self.parent.current_lang]['read_file_error']}{e}")
                self.status_label.setStyleSheet("color: red")
                self.copy_button.setEnabled(True)
        else:
            self.status_label.setText(STRINGS[self.parent.current_lang]['no_files_available'])
            self.status_label.setStyleSheet("color: red")

    def export_conversation(self):
        history_dir = os.path.join(os.getcwd(), "history")
        if not os.path.exists(history_dir):
            os.makedirs(history_dir)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.txt"
        filepath = os.path.join(history_dir, filename)

        original_prefix = src.gui.prefix.get_original_prefix() if src.config.config.USE_PREDEFINED_PREFIX else ""
        transcript_content = ""
        directory = self.folder_edit.text()
        latest_file = src.gui.utils.get_latest_file(directory)
        if latest_file and src.config.config.USE_TRANSCRIPT_TEXT:
            try:
                with open(latest_file, 'r', encoding='utf-8') as file:
                    transcript_content = file.read()
            except Exception as e:
                self.status_label.setText(f"{STRINGS[self.parent.current_lang]['read_file_error']}{e}")
                self.status_label.setStyleSheet("color: red")
                return

        prompt = f"{original_prefix}\n{self.prefix_text.toPlainText()}\n{transcript_content}\n{self.suffix_text.toPlainText()}\n{self.ocr_text_edit.toPlainText()}"
        output = self.output_text.toPlainText()

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Prompt:\n{prompt}\n\nOutput:\n{output}")
            self.status_label.setText(f"{STRINGS[self.parent.current_lang]['export_success']}\n{STRINGS[self.parent.current_lang]['file_path']}{filepath}")
            self.status_label.setStyleSheet("color: green")
        except Exception as e:
            self.status_label.setText(f"{STRINGS[self.parent.currentlang]['export_error']}{e}")
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
        self.export_button.setText(STRINGS[self.parent.current_lang]['export_conversation'])
        self.ocr_button.setText(STRINGS[self.parent.current_lang]['ocr_screenshot'])
        self.ocr_text_label.setText(STRINGS[self.parent.current_lang]['ocr_text'])

class SelectionOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QColor(100, 100, 100, 150))
        painter.setBrush(QColor(100, 100, 100, 50))
        rect = self.rect()
        painter.drawRect(rect)