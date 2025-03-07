from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QSplitter, QTabWidget)
from PyQt6.QtCore import Qt
import os
import datetime
import src.config.config
from src.gui.lang import STRINGS
import src.gui.utils
import src.api.api
import src.gui.prefix
from src.gui.settings_tab import SettingsTab
from src.gui.input_tab import InputTab
from src.gui.output_area import OutputArea

class ContentArea(QWidget):
    """内容区域，负责整合设置选项卡、输入选项卡和输出区域"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        # 创建主垂直布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 5, 10, 5)  # 增加左侧边距
        
        # 创建上下分割的布局
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setObjectName("mainSplitter")
        
        # ========== 创建上半部分区域 ==========
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        spacing = int(src.config.config.UI_SPACING.replace("px", ""))
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(spacing)
        
        # 创建选项卡，将设置和输入内容分开
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("tabWidget")
        
        # ===== 选项卡1: 基本设置 =====
        self.settings_tab = SettingsTab(self.parent)
        self.tab_widget.addTab(self.settings_tab, STRINGS[self.parent.current_lang]['tab_settings'])
        
        # ===== 选项卡2: 输入内容 =====
        self.input_tab = InputTab(self.parent)
        self.tab_widget.addTab(self.input_tab, STRINGS[self.parent.current_lang]['tab_input'])
        
        top_layout.addWidget(self.tab_widget)
        
        # ========== 创建下半部分区域 ==========
        self.output_area = OutputArea(self.parent)
        
        # 将上下部件添加到分割器
        splitter.addWidget(top_widget)
        splitter.addWidget(self.output_area)
        
        # 设置分割器的初始大小比例，调整为更有利于输出显示的比例 (上部:下部 = 2:5)
        splitter.setSizes([200, 500])
        
        # 将分割器添加到主布局
        main_layout.addWidget(splitter)
        
        # 连接信号
        self.output_area.copy_button.clicked.connect(self.copy_and_get_answer)
        self.output_area.export_requested.connect(self.export_conversation)
        
    def apply_theme(self):
        """应用主题样式"""
        theme = src.config.config.THEMES[self.parent.current_theme]
        font_family = src.config.config.UI_FONT_FAMILY
        border_radius = src.config.config.UI_BORDER_RADIUS
        
        self.settings_tab.apply_theme(theme)
        self.input_tab.apply_theme(theme)
        self.output_area.apply_theme(theme)
        
        self.setStyleSheet(f"""
            QWidget {{
                font-family: {font_family};
            }}
            
            #mainSplitter::handle {{
                background-color: {theme['input_border']};
                height: 1px;
            }}
            
            QTabWidget::pane {{
                border: 1px solid {theme['input_border']};
                background-color: {theme['input_bg']};
                border-radius: {border_radius};
            }}
            
            QTabBar::tab {{
                background-color: {theme['tab_bg']};
                color: {theme['tab_text']};
                padding: 6px 12px;
                margin-right: 2px;
                border: 1px solid {theme['input_border']};
                border-bottom: none;
                border-top-left-radius: {border_radius};
                border-top-right-radius: {border_radius};
            }}
            
            QTabBar::tab:selected {{
                background-color: {theme['tab_active_bg']};
                border-bottom-color: {theme['tab_active_bg']};
            }}
        """)

    def select_folder(self):
        """选择文件夹"""
        self.settings_tab.select_folder()

    def copy_and_get_answer(self):
        """复制内容并从API获取回答"""
        directory = self.settings_tab.get_folder_path()
        latest_file = src.gui.utils.get_latest_file(directory)
        original_prefix = src.gui.prefix.get_original_prefix() if src.config.config.USE_PREDEFINED_PREFIX else ""
        ocr_text = self.input_tab.get_ocr_text()

        if latest_file:
            try:
                transcript_content = ""
                if src.config.config.USE_TRANSCRIPT_TEXT:
                    with open(latest_file, 'r', encoding='utf-8') as file:
                        transcript_content = file.read()

                combined_content = f"{original_prefix}\n{self.input_tab.get_prefix_text()}\n{transcript_content}\n{self.input_tab.get_suffix_text()}\n{ocr_text}"
                src.gui.utils.copy_to_clipboard(combined_content)
                self.output_area.set_status(f"{STRINGS[self.parent.current_lang]['copied_success']}\n{STRINGS[self.parent.current_lang]['file_path']}{latest_file}")

                self.output_area.copy_button.setEnabled(False)
                
                # 清空旧内容
                self.output_area.clear_output()
                
                # 使用API获取回答 - 使用多图像功能
                src.api.api.fetch_model_response(
                    combined_content, 
                    self.output_area,
                    self.settings_tab.get_selected_model(), 
                    self.settings_tab.get_temperature(),
                    self.input_tab.get_image_paths()  # 使用新的获取多图像方法
                )
                self.output_area.copy_button.setEnabled(True)

            except Exception as e:
                self.output_area.set_status(f"{STRINGS[self.parent.current_lang]['read_file_error']}{e}", True)
                self.output_area.copy_button.setEnabled(True)
        else:
            self.output_area.set_status(STRINGS[self.parent.current_lang]['no_files_available'], True)

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
        directory = self.settings_tab.get_folder_path()
        latest_file = src.gui.utils.get_latest_file(directory)
        if latest_file and src.config.config.USE_TRANSCRIPT_TEXT:
            try:
                with open(latest_file, 'r', encoding='utf-8') as file:
                    transcript_content = file.read()
            except Exception as e:
                self.output_area.set_status(f"{STRINGS[self.parent.current_lang]['read_file_error']}{e}", True)
                return

        prompt = f"{original_prefix}\n{self.input_tab.get_prefix_text()}\n{transcript_content}\n{self.input_tab.get_suffix_text()}\n{self.input_tab.get_ocr_text()}"
        output = self.output_area.output_text.toPlainText()
        
        # 更新图片信息导出
        image_info = ""
        image_paths = self.input_tab.get_image_paths()
        if image_paths and len(image_paths) > 0:
            image_info = "\n\nImages included:"
            for idx, img_path in enumerate(image_paths):
                image_info += f"\n{idx+1}. {img_path}"

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Prompt:\n{prompt}\n{image_info}\n\nOutput:\n{output}")
            self.output_area.set_status(f"{STRINGS[self.parent.current_lang]['export_success']}\n{STRINGS[self.parent.current_lang]['file_path']}{filepath}")
        except Exception as e:
            self.output_area.set_status(f"{STRINGS[self.parent.current_lang]['export_error']}{e}", True)

    def update_model_list(self, include_local=False):
        """更新模型列表"""
        self.settings_tab.update_model_list(include_local)

    def update_texts(self):
        """更新界面上的文本为当前语言"""
        # 更新选项卡标题
        for i, title in enumerate([STRINGS[self.parent.current_lang]['tab_settings'], STRINGS[self.parent.current_lang]['tab_input']]):
            self.tab_widget.setTabText(i, title)
            
        # 更新各个组件的文本
        self.settings_tab.update_texts()
        self.input_tab.update_texts()
        self.output_area.update_texts()
        
    def on_provider_changed(self, provider):
        """处理提供商选择变更"""
        self.settings_tab.on_provider_changed(provider)