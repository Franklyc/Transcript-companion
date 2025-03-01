from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                           QPushButton, QComboBox, QTextEdit, QFileDialog, QMessageBox, QSplitter,
                           QTabWidget, QScrollArea, QGridLayout, QDialog, QTextBrowser)
from PyQt6.QtCore import Qt, QTimer
import os
import datetime
import src.config.config
from src.gui.lang import STRINGS
import src.gui.utils
import src.api.api
import src.gui.prefix
from src.gui.screenshot_dialog import ScreenshotDialog
from src.gui.image_utils import (display_image, process_ocr, process_screenshot, 
                               upload_image, clear_image, start_screenshot_dialog)
from src.gui.markdown_viewer import render_markdown, append_markdown_text

class ContentArea(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.ocr_enabled = False
        self.screenshot_enabled = False
        self.current_image_path = None
        self.raw_output_text = ""
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
        settings_widget = self._create_settings_tab()
        tab_widget.addTab(settings_widget, STRINGS[self.parent.current_lang]['tab_settings'])
        
        # ===== 选项卡2: 输入内容 =====
        input_widget = self._create_input_tab()
        tab_widget.addTab(input_widget, STRINGS[self.parent.current_lang]['tab_input'])
        
        top_layout.addWidget(tab_widget)
        
        # ========== 创建下半部分区域 ==========
        bottom_widget = self._create_output_area()
        
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

    def _create_settings_tab(self):
        """创建设置选项卡的内容"""
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.setContentsMargins(5, 5, 5, 5)
        settings_layout.setSpacing(3)
        
        # 创建网格布局
        grid_layout = QGridLayout()
        grid_layout.setVerticalSpacing(3)
        
        # 文件夹选择
        self.folder_edit = QLineEdit(src.config.config.DEFAULT_FOLDER_PATH)
        self.folder_edit.setReadOnly(True)
        self.folder_button = QPushButton(STRINGS[self.parent.current_lang]['select_folder'])
        self.folder_button.setFixedHeight(28)
        self.folder_label = QLabel(STRINGS[self.parent.current_lang]['current_folder'])
        grid_layout.addWidget(self.folder_label, 0, 0)
        grid_layout.addWidget(self.folder_edit, 0, 1)
        grid_layout.addWidget(self.folder_button, 0, 2)
        
        # 提供商选择
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(src.config.config.PROVIDERS)
        self.provider_combo.setCurrentText(src.config.config.DEFAULT_PROVIDER)
        self.provider_combo.setFixedHeight(28)
        self.provider_label = QLabel(STRINGS[self.parent.current_lang].get('select_provider', 'Select Provider:'))
        grid_layout.addWidget(self.provider_label, 1, 0)
        grid_layout.addWidget(self.provider_combo, 1, 1, 1, 2)
        
        # 模型选择
        self.model_combo = QComboBox()
        self.model_combo.setFixedHeight(28)
        self.update_model_list(include_local=False)
        self.model_label = QLabel(STRINGS[self.parent.current_lang]['select_model'])
        grid_layout.addWidget(self.model_label, 2, 0)
        grid_layout.addWidget(self.model_combo, 2, 1, 1, 2)
        
        # 温度设置
        self.temp_edit = QLineEdit(src.config.config.DEFAULT_TEMPERATURE)
        self.temp_edit.setFixedHeight(28)
        self.temp_label = QLabel(STRINGS[self.parent.current_lang]['set_temperature'])
        grid_layout.addWidget(self.temp_label, 3, 0)
        grid_layout.addWidget(self.temp_edit, 3, 1, 1, 2)
        
        settings_layout.addLayout(grid_layout)
        return settings_widget

    def _create_input_tab(self):
        """创建输入选项卡的内容"""
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        input_layout.setContentsMargins(5, 5, 5, 5)
        input_layout.setSpacing(3)
        
        # 自定义前缀/后缀
        prefix_suffix_layout = self._create_prefix_suffix_section()
        input_layout.addLayout(prefix_suffix_layout)
        
        # 图像功能区
        image_section = self._create_image_section()
        input_layout.addWidget(image_section)
        
        return input_widget

    def _create_prefix_suffix_section(self):
        """创建前缀/后缀部分"""
        prefix_suffix_layout = QHBoxLayout()
        prefix_suffix_layout.setSpacing(5)
        
        # 前缀
        prefix_container = QWidget()
        prefix_container_layout = QVBoxLayout(prefix_container)
        prefix_container_layout.setContentsMargins(0, 0, 0, 0)
        prefix_container_layout.setSpacing(2)
        self.prefix_label = QLabel(STRINGS[self.parent.current_lang]['custom_prefix'])
        self.prefix_text = QTextEdit()
        self.prefix_text.setMaximumHeight(50)
        prefix_container_layout.addWidget(self.prefix_label)
        prefix_container_layout.addWidget(self.prefix_text)
        prefix_suffix_layout.addWidget(prefix_container)
        
        # 后缀
        suffix_container = QWidget()
        suffix_container_layout = QVBoxLayout(suffix_container)
        suffix_container_layout.setContentsMargins(0, 0, 0, 0)
        suffix_container_layout.setSpacing(2)
        self.suffix_label = QLabel(STRINGS[self.parent.current_lang]['custom_suffix'])
        self.suffix_text = QTextEdit()
        self.suffix_text.setMaximumHeight(50)
        suffix_container_layout.addWidget(self.suffix_label)
        suffix_container_layout.addWidget(self.suffix_text)
        prefix_suffix_layout.addWidget(suffix_container)
        
        return prefix_suffix_layout

    def _create_image_section(self):
        """创建图像处理部分"""
        image_section = QWidget()
        image_section_layout = QVBoxLayout(image_section)
        image_section_layout.setContentsMargins(0, 0, 0, 0)
        image_section_layout.setSpacing(3)
        
        # 图像按钮行
        image_buttons_layout = QHBoxLayout()
        image_buttons_layout.setSpacing(3)
        
        # OCR功能
        self.ocr_button = QPushButton(STRINGS[self.parent.current_lang]['ocr_screenshot'])
        self.ocr_button.setFixedHeight(28)
        self.ocr_button.clicked.connect(self.enable_ocr)
        image_buttons_layout.addWidget(self.ocr_button)
        
        # 图像上传功能
        self.image_upload_button = QPushButton(STRINGS[self.parent.current_lang]['image_upload'])
        self.image_upload_button.setFixedHeight(28)
        self.image_upload_button.clicked.connect(self.upload_image)
        image_buttons_layout.addWidget(self.image_upload_button)
        
        # 截图功能
        self.screenshot_button = QPushButton(STRINGS[self.parent.current_lang]['screenshot_capture'])
        self.screenshot_button.setFixedHeight(28)
        self.screenshot_button.clicked.connect(self.enable_screenshot)
        image_buttons_layout.addWidget(self.screenshot_button)
        
        # 清除图像按钮
        self.clear_image_button = QPushButton(STRINGS[self.parent.current_lang]['image_clear'])
        self.clear_image_button.setFixedHeight(28)
        self.clear_image_button.clicked.connect(self.clear_image)
        image_buttons_layout.addWidget(self.clear_image_button)
        
        image_section_layout.addLayout(image_buttons_layout)
        
        # 图像预览和OCR文本的水平布局
        image_ocr_layout = self._create_image_ocr_layout()
        image_section_layout.addLayout(image_ocr_layout)
        
        return image_section

    def _create_image_ocr_layout(self):
        """创建图像预览和OCR文本区域"""
        image_ocr_layout = QHBoxLayout()
        image_ocr_layout.setSpacing(5)
        
        # 图像预览
        image_preview_container = QWidget()
        image_preview_layout = QVBoxLayout(image_preview_container)
        image_preview_layout.setContentsMargins(0, 0, 0, 0)
        image_preview_layout.setSpacing(2)
        self.image_preview_label = QLabel(STRINGS[self.parent.current_lang]['image_preview'])
        self.image_display = QLabel()
        self.image_display.setMinimumSize(200, 80)
        self.image_display.setMaximumHeight(100)
        self.image_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_display.setStyleSheet("border: 1px solid #CCCCCC;")
        image_preview_layout.addWidget(self.image_preview_label)
        image_preview_layout.addWidget(self.image_display)
        image_ocr_layout.addWidget(image_preview_container)
        
        # OCR文本
        ocr_container = QWidget()
        ocr_layout = QVBoxLayout(ocr_container)
        ocr_layout.setContentsMargins(0, 0, 0, 0)
        ocr_layout.setSpacing(2)
        self.ocr_text_label = QLabel(STRINGS[self.parent.current_lang]['ocr_text'])
        self.ocr_text_edit = QTextEdit()
        self.ocr_text_edit.setMaximumHeight(100)
        ocr_layout.addWidget(self.ocr_text_label)
        ocr_layout.addWidget(self.ocr_text_edit)
        image_ocr_layout.addWidget(ocr_container)
        
        return image_ocr_layout

    def _create_output_area(self):
        """创建输出区域"""
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(3)
        
        # 状态标签
        self.status_label = QLabel()
        self.status_label.setObjectName("status_label")
        self.status_label.setMaximumHeight(40)
        bottom_layout.addWidget(self.status_label)
        
        # 输出文本区域 - 使用QTextBrowser以支持显示HTML/Markdown
        self.output_label = QLabel(STRINGS[self.parent.current_lang]['output_result'])
        
        # 创建一个带有标签的水平布局
        output_header_layout = QHBoxLayout()
        output_header_layout.setSpacing(5)
        output_header_layout.addWidget(self.output_label)
        
        # 添加显示模式切换按钮
        self.toggle_markdown_button = QPushButton("Markdown")
        self.toggle_markdown_button.setCheckable(True)
        self.toggle_markdown_button.setChecked(True)
        self.toggle_markdown_button.clicked.connect(self.toggle_markdown_display)
        self.toggle_markdown_button.setFixedWidth(120)
        self.toggle_markdown_button.setFixedHeight(28)
        output_header_layout.addStretch()
        output_header_layout.addWidget(self.toggle_markdown_button)
        
        bottom_layout.addLayout(output_header_layout)
        
        # 替换QTextEdit为QTextBrowser
        self.output_text = QTextBrowser()
        self.output_text.setOpenExternalLinks(True)
        self.output_text.setStyleSheet("font-size: 12pt;")
        bottom_layout.addWidget(self.output_text)
        
        # 底部按钮布局
        buttons_layout = self._create_bottom_buttons()
        bottom_layout.addLayout(buttons_layout)
        
        return bottom_widget

    def _create_bottom_buttons(self):
        """创建底部按钮区域"""
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(5)
        
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
        
        return buttons_layout

    def update_model_list(self, include_local=False):
        """更新模型列表"""
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
        """启用OCR功能"""
        self.ocr_enabled = False
        self.screenshot_enabled = False
        self.parent.showMinimized()
        
        # Small delay to allow window to minimize
        QTimer.singleShot(300, lambda: start_screenshot_dialog(self, "ocr"))

    def enable_screenshot(self):
        """启用截图功能"""
        self.screenshot_enabled = False
        self.ocr_enabled = False
        self.parent.showMinimized()
        
        # Small delay to allow window to minimize
        QTimer.singleShot(300, lambda: start_screenshot_dialog(self, "screenshot"))

    def upload_image(self):
        """上传图像"""
        upload_image(self)

    def clear_image(self):
        """清除图像"""
        clear_image(self)

    def copy_and_get_answer(self):
        """复制内容并从API获取回答"""
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
                
                # 使用API获取回答
                src.api.api.fetch_model_response(
                    combined_content, 
                    self,
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

    def append_text(self, text):
        """API调用将使用此方法来添加文本"""
        self.raw_output_text = append_markdown_text(
            self.output_text,
            self.raw_output_text,
            text,
            self.toggle_markdown_button.isChecked(),
            self.parent.current_theme == "dark"
        )

    def clear_output(self):
        """清空输出区域"""
        self.output_text.clear()
        self.raw_output_text = ""

    def toggle_markdown_display(self):
        """切换Markdown和纯文本显示模式"""
        is_markdown = self.toggle_markdown_button.isChecked()
        if is_markdown:
            self.toggle_markdown_button.setText("Markdown")
            # 将原始文本转换为HTML并显示
            render_markdown(self.output_text, self.raw_output_text, self.parent.current_theme == "dark")
        else:
            self.toggle_markdown_button.setText(STRINGS[self.parent.current_lang]['show_source'])
            # 显示原始文本
            self.output_text.setPlainText(self.raw_output_text)

    def export_conversation(self):
        """导出当前对话"""
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
        """更新界面上的文本为当前语言"""
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
        
        # 更新选项卡标题
        for i, title in enumerate([STRINGS[self.parent.current_lang]['tab_settings'], STRINGS[self.parent.current_lang]['tab_input']]):
            self.findChild(QTabWidget).setTabText(i, title)
            
        # 更新输出标签
        self.output_label.setText(STRINGS[self.parent.current_lang]['output_result'])
        
        # 更新Markdown切换按钮文本
        if not self.toggle_markdown_button.isChecked():
            self.toggle_markdown_button.setText(STRINGS[self.parent.current_lang]['show_source'])
        else:
            self.toggle_markdown_button.setText("Markdown")