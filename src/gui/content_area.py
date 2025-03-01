from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                           QPushButton, QComboBox, QTextEdit, QFileDialog, QMessageBox, QSplitter,
                           QTabWidget, QScrollArea, QGridLayout, QDialog, QTextBrowser)
from PyQt6.QtGui import QScreen, QPixmap, QPainter, QColor, QGuiApplication, QCursor
from PyQt6.QtCore import Qt, QRect, QPoint, QSize, QTimer
import src.config.config
from src.gui.lang import STRINGS
import src.gui.utils
import src.api.api
import src.gui.prefix
import os
import datetime
import textract
from PIL import Image
import markdown

class ScreenshotDialog(QDialog):
    def __init__(self, parent=None, mode="screenshot"):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(0.3)
        self.setGeometry(QGuiApplication.primaryScreen().geometry())
        self.setCursor(Qt.CursorShape.CrossCursor)
        
        self.mode = mode
        self.start_point = None
        self.end_point = None
        self.selection_rect = QRect()
        self.is_selecting = False
        
        self.setMouseTracking(True)
        
        # Add an instruction label
        self.instruction = QLabel(STRINGS[parent.parent.current_lang]['screenshot_instructions' if mode == 'screenshot' else 'ocr_instructions'])
        self.instruction.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 150); padding: 10px; border-radius: 5px;")
        self.instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.instruction, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch()

    def paintEvent(self, event):
        painter = QPainter(self)
        
        # Draw semi-transparent overlay
        painter.fillRect(self.rect(), QColor(0, 0, 0, 30))
        
        # Draw selection rectangle if we're selecting
        if self.is_selecting and not self.selection_rect.isEmpty():
            # Draw the selection rectangle with a border
            painter.setPen(QColor(0, 162, 232, 255))  # Blue border
            painter.setBrush(QColor(0, 162, 232, 30))  # Semi-transparent blue fill
            painter.drawRect(self.selection_rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.position().toPoint()
            self.is_selecting = True
            self.selection_rect = QRect()
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_selecting and self.start_point:
            self.end_point = event.position().toPoint()
            self.selection_rect = QRect(self.start_point, self.end_point).normalized()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_selecting:
            self.end_point = event.position().toPoint()
            self.selection_rect = QRect(self.start_point, self.end_point).normalized()
            self.is_selecting = False
            
            if self.selection_rect.width() > 10 and self.selection_rect.height() > 10:
                # Take the screenshot with a small delay to allow dialog to hide
                QTimer.singleShot(200, self.take_screenshot)
            else:
                self.reject()  # Cancel if the selection is too small

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        super().keyPressEvent(event)

    def take_screenshot(self):
        if not self.selection_rect.isValid() or self.selection_rect.isEmpty():
            self.reject()
            return
            
        screen = QGuiApplication.primaryScreen()
        screenshot = screen.grabWindow(0, self.selection_rect.x(), self.selection_rect.y(), 
                                      self.selection_rect.width(), self.selection_rect.height())
        
        # Create temp directory if needed
        temp_dir = os.path.join(os.getcwd(), "temp")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            
        # Save the screenshot
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        image_path = os.path.join(temp_dir, f"screenshot_{timestamp}.png")
        screenshot.save(image_path)
        
        # Pass the image path back through accept()
        self.image_path = image_path
        self.accept()

class ContentArea(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.ocr_enabled = False
        self.screenshot_enabled = False
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.selection_overlay = None
        self.current_image_path = None
        self.init_ui()

    def create_labeled_layout(self, label_text, widget):
        """Create a horizontal layout with a label and widget"""
        layout = QHBoxLayout()
        label = QLabel(label_text)
        layout.addWidget(label)
        layout.addWidget(widget)
        return layout, label

    def init_ui(self):
        # 创建主垂直布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 5)
        
        # 创建上下分割的布局
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # ========== 创建上半部分区域 ==========
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(3)  # 减少垂直间距
        
        # 创建选项卡，将设置和输入内容分开
        tab_widget = QTabWidget()
        
        # ===== 选项卡1: 基本设置 =====
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.setContentsMargins(5, 5, 5, 5)  # 减少内边距
        settings_layout.setSpacing(3)  # 减少垂直间距
        
        # 创建网格布局，更紧凑地显示基本设置
        grid_layout = QGridLayout()
        grid_layout.setVerticalSpacing(3)  # 减少垂直间距
        
        # 文件夹选择
        self.folder_edit = QLineEdit(src.config.config.DEFAULT_FOLDER_PATH)
        self.folder_edit.setReadOnly(True)
        self.folder_button = QPushButton(STRINGS[self.parent.current_lang]['select_folder'])
        self.folder_button.setFixedHeight(28)  # 减少按钮高度
        self.folder_label = QLabel(STRINGS[self.parent.current_lang]['current_folder'])
        grid_layout.addWidget(self.folder_label, 0, 0)
        grid_layout.addWidget(self.folder_edit, 0, 1)
        grid_layout.addWidget(self.folder_button, 0, 2)
        
        # 提供商选择
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(src.config.config.PROVIDERS)
        self.provider_combo.setCurrentText(src.config.config.DEFAULT_PROVIDER)
        self.provider_combo.setFixedHeight(28)  # 减少下拉框高度
        self.provider_label = QLabel(STRINGS[self.parent.current_lang].get('select_provider', 'Select Provider:'))
        grid_layout.addWidget(self.provider_label, 1, 0)
        grid_layout.addWidget(self.provider_combo, 1, 1, 1, 2)
        
        # 模型选择
        self.model_combo = QComboBox()
        self.model_combo.setFixedHeight(28)  # 减少下拉框高度
        self.update_model_list(include_local=False)
        self.model_label = QLabel(STRINGS[self.parent.current_lang]['select_model'])
        grid_layout.addWidget(self.model_label, 2, 0)
        grid_layout.addWidget(self.model_combo, 2, 1, 1, 2)
        
        # 温度设置
        self.temp_edit = QLineEdit(src.config.config.DEFAULT_TEMPERATURE)
        self.temp_edit.setFixedHeight(28)  # 减少输入框高度
        self.temp_label = QLabel(STRINGS[self.parent.current_lang]['set_temperature'])
        grid_layout.addWidget(self.temp_label, 3, 0)
        grid_layout.addWidget(self.temp_edit, 3, 1, 1, 2)
        
        settings_layout.addLayout(grid_layout)
        tab_widget.addTab(settings_widget, "设置")
        
        # ===== 选项卡2: 输入内容 =====
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        input_layout.setContentsMargins(5, 5, 5, 5)  # 减少内边距
        input_layout.setSpacing(3)  # 减少垂直间距
        
        # 自定义前缀/后缀
        prefix_suffix_layout = QHBoxLayout()
        prefix_suffix_layout.setSpacing(5)  # 减少水平间距
        
        # 前缀
        prefix_container = QWidget()
        prefix_container_layout = QVBoxLayout(prefix_container)
        prefix_container_layout.setContentsMargins(0, 0, 0, 0)
        prefix_container_layout.setSpacing(2)  # 减少垂直间距
        self.prefix_label = QLabel(STRINGS[self.parent.current_lang]['custom_prefix'])
        self.prefix_text = QTextEdit()
        self.prefix_text.setMaximumHeight(50)  # 减小前缀文本框高度
        prefix_container_layout.addWidget(self.prefix_label)
        prefix_container_layout.addWidget(self.prefix_text)
        prefix_suffix_layout.addWidget(prefix_container)
        
        # 后缀
        suffix_container = QWidget()
        suffix_container_layout = QVBoxLayout(suffix_container)
        suffix_container_layout.setContentsMargins(0, 0, 0, 0)
        suffix_container_layout.setSpacing(2)  # 减少垂直间距
        self.suffix_label = QLabel(STRINGS[self.parent.current_lang]['custom_suffix'])
        self.suffix_text = QTextEdit()
        self.suffix_text.setMaximumHeight(50)  # 减小后缀文本框高度
        suffix_container_layout.addWidget(self.suffix_label)
        suffix_container_layout.addWidget(self.suffix_text)
        prefix_suffix_layout.addWidget(suffix_container)
        
        input_layout.addLayout(prefix_suffix_layout)
        
        # 图像功能区
        image_section = QWidget()
        image_section_layout = QVBoxLayout(image_section)
        image_section_layout.setContentsMargins(0, 0, 0, 0)
        image_section_layout.setSpacing(3)  # 减少垂直间距
        
        # 图像按钮行
        image_buttons_layout = QHBoxLayout()
        image_buttons_layout.setSpacing(3)  # 减少水平间距
        
        # OCR功能
        self.ocr_button = QPushButton(STRINGS[self.parent.current_lang]['ocr_screenshot'])
        self.ocr_button.setFixedHeight(28)  # 减少按钮高度
        self.ocr_button.clicked.connect(self.enable_ocr)
        image_buttons_layout.addWidget(self.ocr_button)
        
        # 图像上传功能
        self.image_upload_button = QPushButton(STRINGS[self.parent.current_lang]['image_upload'])
        self.image_upload_button.setFixedHeight(28)  # 减少按钮高度
        self.image_upload_button.clicked.connect(self.upload_image)
        image_buttons_layout.addWidget(self.image_upload_button)
        
        # 截图功能
        self.screenshot_button = QPushButton(STRINGS[self.parent.current_lang]['screenshot_capture'])
        self.screenshot_button.setFixedHeight(28)  # 减少按钮高度
        self.screenshot_button.clicked.connect(self.enable_screenshot)
        image_buttons_layout.addWidget(self.screenshot_button)
        
        # 清除图像按钮
        self.clear_image_button = QPushButton(STRINGS[self.parent.current_lang]['image_clear'])
        self.clear_image_button.setFixedHeight(28)  # 减少按钮高度
        self.clear_image_button.clicked.connect(self.clear_image)
        image_buttons_layout.addWidget(self.clear_image_button)
        
        image_section_layout.addLayout(image_buttons_layout)
        
        # 图像预览和OCR文本的水平布局
        image_ocr_layout = QHBoxLayout()
        image_ocr_layout.setSpacing(5)  # 减少水平间距
        
        # 图像预览
        image_preview_container = QWidget()
        image_preview_layout = QVBoxLayout(image_preview_container)
        image_preview_layout.setContentsMargins(0, 0, 0, 0)
        image_preview_layout.setSpacing(2)  # 减少垂直间距
        self.image_preview_label = QLabel(STRINGS[self.parent.current_lang]['image_preview'])
        self.image_display = QLabel()
        self.image_display.setMinimumSize(QSize(150, 80))  # 减少最小高度
        self.image_display.setMaximumHeight(100)  # 减少最大高度
        self.image_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_display.setStyleSheet("border: 1px solid #CCCCCC;")
        image_preview_layout.addWidget(self.image_preview_label)
        image_preview_layout.addWidget(self.image_display)
        image_ocr_layout.addWidget(image_preview_container)
        
        # OCR文本
        ocr_container = QWidget()
        ocr_layout = QVBoxLayout(ocr_container)
        ocr_layout.setContentsMargins(0, 0, 0, 0)
        ocr_layout.setSpacing(2)  # 减少垂直间距
        self.ocr_text_label = QLabel(STRINGS[self.parent.current_lang]['ocr_text'])
        self.ocr_text_edit = QTextEdit()
        self.ocr_text_edit.setMaximumHeight(100)  # 减少最大高度
        ocr_layout.addWidget(self.ocr_text_label)
        ocr_layout.addWidget(self.ocr_text_edit)
        image_ocr_layout.addWidget(ocr_container)
        
        image_section_layout.addLayout(image_ocr_layout)
        input_layout.addWidget(image_section)
        
        tab_widget.addTab(input_widget, "输入")
        
        top_layout.addWidget(tab_widget)
        
        # ========== 创建下半部分区域 ==========
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(3)  # 减少垂直间距
        
        # 状态标签
        self.status_label = QLabel()
        self.status_label.setObjectName("status_label")
        self.status_label.setMaximumHeight(40)  # 限制状态标签高度
        bottom_layout.addWidget(self.status_label)
        
        # 输出文本区域 - 使用QTextBrowser以支持显示HTML/Markdown
        output_label = QLabel("输出结果:")
        
        # 创建一个带有标签的水平布局
        output_header_layout = QHBoxLayout()
        output_header_layout.setSpacing(5)  # 减少水平间距
        output_header_layout.addWidget(output_label)
        
        # 添加显示模式切换按钮
        self.toggle_markdown_button = QPushButton("Markdown")
        self.toggle_markdown_button.setCheckable(True)
        self.toggle_markdown_button.setChecked(True)  # 默认开启Markdown
        self.toggle_markdown_button.clicked.connect(self.toggle_markdown_display)
        self.toggle_markdown_button.setFixedWidth(120)
        self.toggle_markdown_button.setFixedHeight(28)  # 减少按钮高度
        output_header_layout.addStretch()
        output_header_layout.addWidget(self.toggle_markdown_button)
        
        bottom_layout.addLayout(output_header_layout)
        
        # 替换QTextEdit为QTextBrowser
        self.output_text = QTextBrowser()
        self.output_text.setOpenExternalLinks(True)  # 允许打开外部链接
        self.output_text.setStyleSheet("font-size: 12pt;")
        bottom_layout.addWidget(self.output_text)
        
        # 存储原始文本内容
        self.raw_output_text = ""
        
        # 底部按钮布局
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(5)  # 减少水平间距
        
        # 复制按钮
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
        
        # 导出按钮
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
        bottom_layout.addLayout(buttons_layout)
        
        # 将上下部件添加到分割器
        splitter.addWidget(top_widget)
        splitter.addWidget(bottom_widget)
        
        # 设置分割器的初始大小比例，调整为更有利于输出显示的比例 (上部:下部 = 2:5)
        splitter.setSizes([200, 500])
        
        # 将分割器添加到主布局
        main_layout.addWidget(splitter)
        
        # 连接信号
        self.folder_button.clicked.connect(self.select_folder)
        self.copy_button.clicked.connect(self.copy_and_get_answer)
        self.export_button.clicked.connect(self.export_conversation)
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)

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
        if (index >= 0):
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
            QTabWidget::pane {{
                border: 1px solid {theme['input_border']};
                background-color: {theme['input_bg']};
            }}
            QTabBar::tab {{
                background-color: {theme['sidebar_bg']};
                color: {theme['text']};
                padding: 6px 12px;
                margin-right: 2px;
                border: 1px solid {theme['input_border']};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {theme['input_bg']};
                border-bottom-color: {theme['input_bg']};
            }}
        """)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self)
        if folder_path:
            self.folder_edit.setText(folder_path)

    def enable_ocr(self):
        self.ocr_enabled = False  # We'll handle this differently now
        self.screenshot_enabled = False
        self.parent.showMinimized()
        
        # Small delay to allow window to minimize
        QTimer.singleShot(300, lambda: self.start_screenshot_dialog("ocr"))

    def enable_screenshot(self):
        self.screenshot_enabled = False  # We'll handle this differently now
        self.ocr_enabled = False
        self.parent.showMinimized()
        
        # Small delay to allow window to minimize
        QTimer.singleShot(300, lambda: self.start_screenshot_dialog("screenshot"))
        
    def start_screenshot_dialog(self, mode):
        dialog = ScreenshotDialog(self, mode)
        result = dialog.exec()
        
        # Get the main window using the correct reference chain
        main_window = self.parent  # MainWindow instance
        main_window.showNormal()  # Properly restore from minimized state
        main_window.activateWindow()  # Ensure window gets focus
        main_window.raise_()  # Bring it to the front
        
        if result == QDialog.DialogCode.Accepted:
            image_path = dialog.image_path
            if mode == "ocr":
                self.process_ocr(image_path)
            else:
                self.process_screenshot(image_path)
        else:
            mode_text = 'ocr_selection_canceled' if mode == 'ocr' else 'screenshot_canceled'
            self.status_label.setText(STRINGS[self.parent.current_lang][mode_text])
            self.status_label.setStyleSheet("color: orange")
            
    def process_ocr(self, image_path):
        try:
            text = textract.process(image_path).decode('utf-8')
            self.ocr_text_edit.setText(text)
            self.current_image_path = image_path
            self.display_image(image_path)
            self.status_label.setText(STRINGS[self.parent.current_lang]['ocr_success'])
            self.status_label.setStyleSheet("color: green")
        except Exception as e:
            self.status_label.setText(f"{STRINGS[self.parent.current_lang]['ocr_error']}: {e}")
            self.status_label.setStyleSheet("color: red")
            
    def process_screenshot(self, image_path):
        self.current_image_path = image_path
        self.display_image(image_path)
        self.status_label.setText(STRINGS[self.parent.current_lang]['screenshot_success'])
        self.status_label.setStyleSheet("color: green")

    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Image", 
            "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            try:
                self.current_image_path = file_path
                self.display_image(file_path)
                self.status_label.setText(STRINGS[self.parent.current_lang]['image_upload_success'])
                self.status_label.setStyleSheet("color: green")
            except Exception as e:
                self.status_label.setText(f"{STRINGS[self.parent.current_lang]['image_upload_error']}{e}")
                self.status_label.setStyleSheet("color: red")

    def clear_image(self):
        self.image_display.clear()
        self.current_image_path = None
        self.status_label.clear()

    def display_image(self, image_path):
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            # Scale while maintaining aspect ratio
            pixmap = pixmap.scaled(
                self.image_display.width(), 
                self.image_display.maximumHeight(),
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_display.setPixmap(pixmap)

    # The following methods are no longer needed with the new screenshot approach
    # But we'll keep empty implementations for compatibility
    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        pass

    def update_selection_overlay(self):
        pass

    def capture_screenshot(self, mode):
        pass

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
                
                # 清空旧内容
                self.output_text.clear()
                self.raw_output_text = ""
                
                # 使用修改后的回调来支持动态更新Markdown
                src.api.api.fetch_model_response(
                    combined_content, 
                    self,  # 传递self而不是output_text
                    self.model_combo.currentText(), 
                    self.temp_edit.text(),
                    self.current_image_path
                )
                self.copy_button.setEnabled(True)

            except Exception as e:
                self.status_label.setText(f"{STRINGS[self.parent.current_lang]['read_file_error']}{e}")
                self.status_label.setStyleSheet("color: red")
                self.copy_button.setEnabled(True)
        else:
            self.status_label.setText(STRINGS[self.parent.current_lang]['no_files_available'])
            self.status_label.setStyleSheet("color: red")

    # 自定义方法用于API回调
    def append_text(self, text):
        """API调用将使用此方法来添加文本"""
        self.raw_output_text += text
        if self.toggle_markdown_button.isChecked():
            # 更新Markdown渲染
            self.render_markdown(self.raw_output_text)
        else:
            # 直接显示文本
            current_text = self.output_text.toPlainText()
            self.output_text.setPlainText(current_text + text)
        
        # 滚动到底部
        sb = self.output_text.verticalScrollBar()
        sb.setValue(sb.maximum())
        
        # 处理Qt事件循环，确保UI及时更新
        QApplication.processEvents()

    def clear_output(self):
        """清空输出区域"""
        self.output_text.clear()
        self.raw_output_text = ""

    # 添加切换Markdown显示的方法
    def toggle_markdown_display(self):
        is_markdown = self.toggle_markdown_button.isChecked()
        if is_markdown:
            self.toggle_markdown_button.setText("Markdown")
            # 将原始文本转换为HTML并显示
            self.render_markdown(self.raw_output_text)
        else:
            self.toggle_markdown_button.setText("显示源文本")
            # 显示原始文本
            self.output_text.setPlainText(self.raw_output_text)

    # 渲染Markdown的方法
    def render_markdown(self, text):
        if not text:
            return
            
        try:
            # 将Markdown转换为HTML
            html = markdown.markdown(
                text,
                extensions=['tables', 'fenced_code', 'codehilite']
            )
            
            # 添加基本CSS样式
            styled_html = f"""
            <html>
            <head>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; }}
                h1, h2, h3, h4, h5, h6 {{ color: #3B82F6; margin-top: 20px; margin-bottom: 10px; }}
                h1 {{ font-size: 24px; }}
                h2 {{ font-size: 20px; }}
                h3 {{ font-size: 18px; }}
                h4 {{ font-size: 16px; }}
                p {{ margin-bottom: 12px; line-height: 1.6; }}
                code {{ background-color: #F1F5F9; padding: 2px 4px; border-radius: 3px; font-family: Consolas, monospace; }}
                pre {{ background-color: #F1F5F9; padding: 12px; border-radius: 5px; overflow-x: auto; }}
                pre code {{ background-color: transparent; padding: 0; }}
                blockquote {{ border-left: 4px solid #CBD5E1; padding-left: 12px; color: #64748B; margin: 12px 0; }}
                a {{ color: #3B82F6; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
                ul, ol {{ padding-left: 20px; margin-bottom: 12px; }}
                li {{ margin-bottom: 4px; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 12px; }}
                th, td {{ border: 1px solid #E2E8F0; padding: 8px; text-align: left; }}
                th {{ background-color: #F1F5F9; }}
            </style>
            </head>
            <body>{html}</body>
            </html>
            """
            
            # 检查当前主题并应用相应的深色模式样式
            if self.parent.current_theme == "dark":
                styled_html = f"""
                <html>
                <head>
                <style>
                    body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #E2E8F0; }}
                    h1, h2, h3, h4, h5, h6 {{ color: #3B82F6; margin-top: 20px; margin-bottom: 10px; }}
                    h1 {{ font-size: 24px; }}
                    h2 {{ font-size: 20px; }}
                    h3 {{ font-size: 18px; }}
                    h4 {{ font-size: 16px; }}
                    p {{ margin-bottom: 12px; line-height: 1.6; }}
                    code {{ background-color: #1E293B; color: #E2E8F0; padding: 2px 4px; border-radius: 3px; font-family: Consolas, monospace; }}
                    pre {{ background-color: #1E293B; padding: 12px; border-radius: 5px; overflow-x: auto; }}
                    pre code {{ background-color: transparent; padding: 0; }}
                    blockquote {{ border-left: 4px solid #4B5563; padding-left: 12px; color: #94A3B8; margin: 12px 0; }}
                    a {{ color: #60A5FA; text-decoration: none; }}
                    a:hover {{ text-decoration: underline; }}
                    ul, ol {{ padding-left: 20px; margin-bottom: 12px; }}
                    li {{ margin-bottom: 4px; }}
                    table {{ border-collapse: collapse; width: 100%; margin-bottom: 12px; }}
                    th, td {{ border: 1px solid #4B5563; padding: 8px; text-align: left; }}
                    th {{ background-color: #1E293B; }}
                </style>
                </head>
                <body>{html}</body>
                </html>
                """
            
            # 设置HTML内容
            self.output_text.setHtml(styled_html)
        except Exception as e:
            self.output_text.setPlainText(f"Markdown渲染错误: {str(e)}\n\n{text}")

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
        if (latest_file and src.config.config.USE_TRANSCRIPT_TEXT):
            try:
                with open(latest_file, 'r', encoding='utf-8') as file:
                    transcript_content = file.read()
            except Exception as e:
                self.status_label.setText(f"{STRINGS[self.parent.current_lang]['read_file_error']}{e}")
                self.status_label.setStyleSheet("color: red")
                return

        prompt = f"{original_prefix}\n{self.prefix_text.toPlainText()}\n{transcript_content}\n{self.suffix_text.toPlainText()}\n{self.ocr_text_edit.toPlainText()}"
        output = self.output_text.toPlainText()
        
        image_info = ""
        if self.current_image_path:
            image_info = f"\n\nImage was included: {self.current_image_path}"

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Prompt:\n{prompt}\n{image_info}\n\nOutput:\n{output}")
            self.status_label.setText(f"{STRINGS[self.parent.current_lang]['export_success']}\n{STRINGS[self.parent.current_lang]['file_path']}{filepath}")
            self.status_label.setStyleSheet("color: green")
        except Exception as e:
            self.status_label.setText(f"{STRINGS[self.parent.current_lang]['export_error']}{e}")
            self.status_label.setStyleSheet("color: red")

    def update_texts(self):
        # 更新所有文本标签
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
        self.image_upload_button.setText(STRINGS[self.parent.current_lang]['image_upload'])
        self.screenshot_button.setText(STRINGS[self.parent.current_lang]['screenshot_capture'])
        self.clear_image_button.setText(STRINGS[self.parent.current_lang]['image_clear'])
        self.image_preview_label.setText(STRINGS[self.parent.current_lang]['image_preview'])
        
        # 更新Markdown切换按钮文本
        self.toggle_markdown_button.setText("Markdown" if self.toggle_markdown_button.isChecked() else "显示源文本")

class SelectionOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QColor(100, 100, 100, 150))
        painter.setBrush(QColor(100, 100, 100, 50))
        rect = self.rect()
        painter.drawRect(rect)