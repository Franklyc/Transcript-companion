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
        # 初始化对话历史记录
        self.dialogue_history = []
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

    def get_new_transcript_content(self, file_path):
        """获取新增的转录内容（支持连续对话）
        
        返回:
            (新增内容, 是否有新内容)
        """
        try:
            if not os.path.exists(file_path):
                return "", False
                
            # 读取整个文件内容
            with open(file_path, 'r', encoding='utf-8') as file:
                full_content = file.read()
            
            # 如果未启用连续对话功能，直接返回全部内容
            if not src.config.config.ENABLE_CONTINUOUS_DIALOGUE:
                return full_content, True
                
            # 检查是否已有记录的文件位置
            last_position = src.config.config.TRANSCRIPT_POSITION.get(file_path, 0)
            
            # 计算新内容
            if last_position >= len(full_content):
                return "", False  # 没有新内容
                
            new_content = full_content[last_position:]
            
            # 更新文件位置
            src.config.config.TRANSCRIPT_POSITION[file_path] = len(full_content)
            
            self.output_area.set_status(
                STRINGS[self.parent.current_lang]['new_content_detected'].format(len(new_content)) + 
                "\n" + 
                STRINGS[self.parent.current_lang]['resuming_from_position'].format(last_position)
            )
            
            return new_content, len(new_content) > 0
            
        except Exception as e:
            self.output_area.set_status(f"{STRINGS[self.parent.current_lang]['read_file_error']}{e}", True)
            return "", False

    def copy_and_get_answer(self):
        """复制内容并从API获取回答"""
        directory = self.settings_tab.get_folder_path()
        latest_file = src.gui.utils.get_latest_file(directory)
        original_prefix = src.gui.prefix.get_original_prefix() if src.config.config.USE_PREDEFINED_PREFIX else ""
        ocr_text = self.input_tab.get_ocr_text()
        
        # 获取用户自定义的前缀和后缀文本
        prefix_text = self.input_tab.get_prefix_text()
        suffix_text = self.input_tab.get_suffix_text()

        # 检查是否有文件可用
        if not latest_file and not src.config.config.ENABLE_CONTINUOUS_DIALOGUE:
            self.output_area.set_status(STRINGS[self.parent.current_lang]['no_files_available'], True)
            return
            
        try:
            transcript_content = ""
            has_new_content = False
            
            # 获取转录文本内容 - 无论是否为连续对话模式
            if src.config.config.USE_TRANSCRIPT_TEXT and latest_file:
                if src.config.config.ENABLE_CONTINUOUS_DIALOGUE:
                    # 连续对话模式：只获取新内容
                    transcript_content, has_new_content = self.get_new_transcript_content(latest_file)
                else:
                    # 普通模式：获取全部内容
                    try:
                        with open(latest_file, 'r', encoding='utf-8') as file:
                            transcript_content = file.read()
                            has_new_content = bool(transcript_content)
                    except Exception as e:
                        self.output_area.set_status(f"{STRINGS[self.parent.current_lang]['read_file_error']}{e}", True)
                        return
            
            # 确定是否有任何输入内容可用于对话
            has_input_content = bool(transcript_content) or bool(ocr_text) or bool(prefix_text) or bool(suffix_text)
            
            # 处理连续对话的情况
            if src.config.config.ENABLE_CONTINUOUS_DIALOGUE:
                # 即使没有新内容，只要有用户输入或者有历史记录，也可以继续对话
                if not has_input_content and not self.dialogue_history:
                    # 真的什么都没有的情况
                    self.output_area.set_status(STRINGS[self.parent.current_lang]['no_files_available'], True)
                    return
                
                # 连续对话模式：添加对话上下文提示
                context_msg = STRINGS[self.parent.current_lang]['continuous_dialogue_context'].format(len(self.dialogue_history))
                
                # 构建当前提示内容 - 即使转录内容为空，也需要创建包含前缀、后缀的提示
                prompt_parts = []
                
                # 如果有前缀或后缀，始终添加这部分
                if prefix_text or transcript_content or suffix_text:
                    # 构建包含前缀、转录内容、后缀的完整提示
                    full_text_parts = []
                    if prefix_text:
                        full_text_parts.append(prefix_text)
                    if transcript_content:
                        full_text_parts.append(transcript_content)
                    if suffix_text:
                        full_text_parts.append(suffix_text)
                    prompt_parts.append("\n".join(full_text_parts))
                
                # 添加OCR文本(如果有)
                if ocr_text:
                    prompt_parts.append(ocr_text)
                    
                combined_content = "\n".join(prompt_parts)
                
                # 如果没有任何新增内容但有历史记录，允许用户继续对话
                if not combined_content and self.dialogue_history:
                    # 使用一个特殊提示告知模型继续前面的对话
                    combined_content = "Please continue analyzing based on our previous conversation."
                
                # 设置状态并复制到剪贴板
                status_message = context_msg
                if latest_file:
                    status_message += f"\n{STRINGS[self.parent.current_lang]['copied_success']}\n{STRINGS[self.parent.current_lang]['file_path']}{latest_file}"
                
                # 只在有内容时复制到剪贴板
                if combined_content:
                    src.gui.utils.copy_to_clipboard(combined_content)
                    self.output_area.set_status(status_message)
            else:
                # 非连续对话模式，使用完整提示
                # 检查没有转录文件内容且未启用预定义前缀的情况
                if not transcript_content and not src.config.config.USE_PREDEFINED_PREFIX:
                    if not ocr_text and not prefix_text and not suffix_text:
                        self.output_area.set_status(STRINGS[self.parent.current_lang]['no_files_available'], True)
                        return
                        
                combined_content = f"{original_prefix}\n{prefix_text}\n{transcript_content}\n{suffix_text}\n{ocr_text}"
                combined_content = combined_content.strip()
                
                if not combined_content:
                    self.output_area.set_status(STRINGS[self.parent.current_lang]['no_files_available'], True)
                    return
                    
                src.gui.utils.copy_to_clipboard(combined_content)
                
                if latest_file:
                    self.output_area.set_status(f"{STRINGS[self.parent.current_lang]['copied_success']}\n{STRINGS[self.parent.current_lang]['file_path']}{latest_file}")
                else:
                    self.output_area.set_status(f"{STRINGS[self.parent.current_lang]['copied_success']}")

            self.output_area.copy_button.setEnabled(False)
            
            # 清空旧内容
            self.output_area.clear_output()
            
            # 使用API获取回答
            if src.config.config.ENABLE_CONTINUOUS_DIALOGUE:
                # 连续对话模式：传递对话历史和新内容
                src.api.api.fetch_model_response_with_history(
                    combined_content, 
                    self.output_area,
                    self.settings_tab.get_selected_model(), 
                    self.settings_tab.get_temperature(),
                    self.dialogue_history,
                    self.input_tab.get_image_paths()
                )
            else:
                # 传统模式：直接传递完整内容
                src.api.api.fetch_model_response(
                    combined_content, 
                    self.output_area,
                    self.settings_tab.get_selected_model(), 
                    self.settings_tab.get_temperature(),
                    self.input_tab.get_image_paths()
                )
            
            self.output_area.copy_button.setEnabled(True)

        except Exception as e:
            self.output_area.set_status(f"{STRINGS[self.parent.current_lang]['read_file_error']}{e}", True)
            self.output_area.copy_button.setEnabled(True)

    def export_conversation(self):
        """导出当前对话"""
        history_dir = os.path.join(os.getcwd(), "history")
        if not os.path.exists(history_dir):
            os.makedirs(history_dir)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.txt"
        filepath = os.path.join(history_dir, filename)

        # 获取当前会话信息（用于非连续对话模式）
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

        current_prompt = f"{original_prefix}\n{self.input_tab.get_prefix_text()}\n{transcript_content}\n{self.input_tab.get_suffix_text()}\n{self.input_tab.get_ocr_text()}"
        current_output = self.output_area.output_text.toPlainText()
        
        # 获取图片信息
        image_paths = self.input_tab.get_image_paths()
        image_info = []
        if image_paths and len(image_paths) > 0:
            for idx, img_path in enumerate(image_paths):
                image_info.append(f"{idx+1}. {os.path.basename(img_path)}")
        
        # 获取当前语言
        current_lang = self.parent.current_lang
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # 使用当前语言的文本
                heading_conversation = "完整对话历史记录" if current_lang == 'zh' else "Complete Conversation History"
                heading_system = "系统消息" if current_lang == 'zh' else "System Message"
                heading_turn = "轮次" if current_lang == 'zh' else "Turn"
                heading_user = "用户输入" if current_lang == 'zh' else "User Input"
                heading_assistant = "助手回复" if current_lang == 'zh' else "Assistant Response"
                heading_related_images = "相关图片" if current_lang == 'zh' else "Related Images"
                heading_conversation_record = "对话记录" if current_lang == 'zh' else "Conversation Record"
                heading_export_time = "导出时间" if current_lang == 'zh' else "Export Time"
                heading_model = "使用的模型" if current_lang == 'zh' else "Model Used"
                heading_temperature = "温度" if current_lang == 'zh' else "Temperature"
                heading_transcript_file = "转录文件" if current_lang == 'zh' else "Transcript File"
                heading_mode = "模式" if current_lang == 'zh' else "Mode"
                text_continuous = "连续对话" if current_lang == 'zh' else "Continuous Dialogue"
                text_single = "单次对话" if current_lang == 'zh' else "Single Dialogue"
                
                # 如果启用了连续对话，输出完整的对话历史
                if src.config.config.ENABLE_CONTINUOUS_DIALOGUE and self.dialogue_history:
                    f.write(f"# {heading_conversation}\n\n")
                    
                    # 整理系统消息、用户消息和助手消息
                    current_turn = 0
                    for i, (role, content) in enumerate(self.dialogue_history):
                        if role == "system":
                            f.write(f"## {heading_system}\n{content}\n\n")
                        elif role == "user":
                            current_turn += 1
                            f.write(f"## {heading_turn} {current_turn} - {heading_user}\n{content}\n\n")
                            
                            # 检查此用户消息是否关联了图片
                            if i > 0 and i < len(self.dialogue_history) - 1:
                                # 简单的图片关联启发式：如果输入很短且包含图片路径关键词
                                image_keywords = ["image", "图片", "截图", "picture", "screenshot", "photo"]
                                has_image_keyword = any(keyword in content.lower() for keyword in image_keywords)
                                if has_image_keyword and image_info:
                                    f.write(f"### {heading_related_images}\n")
                                    for img in image_info:
                                        f.write(f"- {img}\n")
                                    f.write("\n")
                        elif role == "assistant":
                            f.write(f"## {heading_turn} {current_turn} - {heading_assistant}\n{content}\n\n")
                            f.write("---\n\n")  # 分隔符
                else:
                    # 非连续对话模式下，只导出当前的对话
                    f.write(f"# {heading_conversation_record}\n\n")
                    
                    f.write(f"## {heading_user}\n")
                    f.write(f"{current_prompt}\n\n")
                    
                    # 添加图片信息
                    if image_info:
                        f.write(f"### {heading_related_images}\n")
                        for img in image_info:
                            f.write(f"- {img}\n")
                        f.write("\n")
                        
                    f.write(f"## {heading_assistant}\n")
                    f.write(f"{current_output}\n\n")
                    
                # 添加元数据
                f.write("---\n\n")
                f.write(f"{heading_export_time}: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{heading_model}: {self.settings_tab.get_selected_model()}\n")
                f.write(f"{heading_temperature}: {self.settings_tab.get_temperature()}\n")
                if latest_file:
                    f.write(f"{heading_transcript_file}: {latest_file}\n")
                if src.config.config.ENABLE_CONTINUOUS_DIALOGUE:
                    f.write(f"{heading_mode}: {text_continuous}\n")
                else:
                    f.write(f"{heading_mode}: {text_single}\n")
                    
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