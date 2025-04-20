from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QSplitter, QTabWidget)
from PyQt6.QtCore import Qt, QThread, pyqtSlot
import os
import datetime
import src.config.config
from src.gui.lang import STRINGS
import src.gui.utils
# import src.api.api # No longer needed directly for fetching
from src.api.worker import ApiWorker # Import the worker
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
        self.api_thread = None
        self.api_worker = None
        # Store the prompt that was sent for history update later
        self._current_prompt_for_history = ""
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
        self.output_area.copy_button.clicked.connect(self.start_api_request) # Connect to the new start method
        self.output_area.stop_button.clicked.connect(self.stop_api_request) # Connect stop button
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
                border: 1px solid {theme['glass_border']};
                background-color: {theme['input_bg']};
                border-radius: {border_radius};
            }}
            
            QTabBar::tab {{
                background-color: {theme['tab_bg']};
                color: {theme['tab_text']};
                padding: 8px 14px;
                margin-right: 4px;
                border: 1px solid {theme['glass_border']};
                border-bottom: none;
                border-top-left-radius: {border_radius};
                border-top-right-radius: {border_radius};
            }}
            
            QTabBar::tab:selected {{
                background-color: {theme['tab_active_bg']};
                border-bottom-color: {theme['tab_active_bg']};
                border-bottom-width: 2px;
                border-bottom-style: solid;
            }}
            
            QTabBar::tab:hover:!selected {{
                background-color: rgba(255, 255, 255, 0.1);
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

    def start_api_request(self):
        """准备并启动后台 API 请求"""
        if self.api_thread is not None and self.api_thread.isRunning():
            # Optionally: Stop the previous request or show a message
            print("API request already in progress.")
            # self.stop_api_request() # Or implement stopping logic
            return

        directory = self.settings_tab.get_folder_path()
        latest_file = src.gui.utils.get_latest_file(directory)
        original_prefix = src.gui.prefix.get_original_prefix() if src.config.config.USE_PREDEFINED_PREFIX else ""
        ocr_text = self.input_tab.get_ocr_text()
        prefix_text = self.input_tab.get_prefix_text()
        suffix_text = self.input_tab.get_suffix_text()
        image_paths = self.input_tab.get_image_paths() # Get image paths
        model_name = self.settings_tab.get_selected_model()
        temperature = self.settings_tab.get_temperature()
        use_history_mode = src.config.config.ENABLE_CONTINUOUS_DIALOGUE

        # --- Logic to prepare combined_content (similar to original) ---
        transcript_content = ""
        if src.config.config.USE_TRANSCRIPT_TEXT and latest_file:
            try:
                if use_history_mode:
                    transcript_content, _ = self.get_new_transcript_content(latest_file)
                else:
                    with open(latest_file, 'r', encoding='utf-8') as file:
                        transcript_content = file.read()
            except Exception as e:
                self.output_area.set_status(f"{STRINGS[self.parent.current_lang]['read_file_error']}{e}", True)
                return

        # Determine combined content based on mode
        if use_history_mode:
            prompt_parts = []
            if prefix_text or transcript_content or suffix_text:
                full_text_parts = [part for part in [prefix_text, transcript_content, suffix_text] if part]
                prompt_parts.append("\n".join(full_text_parts))
            if ocr_text:
                prompt_parts.append(ocr_text)
            combined_content = "\n".join(prompt_parts)

            # Handle case where only history exists for continuous dialogue
            if not combined_content and self.dialogue_history:
                combined_content = "Please continue analyzing based on our previous conversation." # Special prompt

            # Check if there's anything to send
            if not combined_content and not self.dialogue_history:
                 self.output_area.set_status(STRINGS[self.parent.current_lang]['no_files_available'], True)
                 return

            # Set status message for continuous mode
            context_msg = STRINGS[self.parent.current_lang]['continuous_dialogue_context'].format(len(self.dialogue_history))
            status_message = context_msg
            if latest_file:
                 status_message += f"\n{STRINGS[self.parent.current_lang]['copied_success']}\n{STRINGS[self.parent.current_lang]['file_path']}{latest_file}"
            if combined_content: # Only copy if there's new content
                 src.gui.utils.copy_to_clipboard(combined_content)
            self.output_area.set_status(status_message)

        else: # Not continuous dialogue mode
            combined_content = f"{original_prefix}\n{prefix_text}\n{transcript_content}\n{suffix_text}\n{ocr_text}"
            combined_content = combined_content.strip()

            if not combined_content and not image_paths: # Check if there's any input at all
                self.output_area.set_status(STRINGS[self.parent.current_lang]['no_files_available'], True)
                return

            src.gui.utils.copy_to_clipboard(combined_content) # Copy combined text
            if latest_file:
                self.output_area.set_status(f"{STRINGS[self.parent.current_lang]['copied_success']}\n{STRINGS[self.parent.current_lang]['file_path']}{latest_file}")
            else:
                self.output_area.set_status(f"{STRINGS[self.parent.current_lang]['copied_success']}")

        # --- Start Background Task ---
        self.output_area.copy_button.setVisible(False) # Hide copy button
        self.output_area.stop_button.setVisible(True)  # Show stop button
        self.output_area.stop_button.setEnabled(True)
        self.output_area.clear_output()
        self.output_area.set_status(STRINGS[self.parent.current_lang]['fetching_response']) # Indicate fetching

        # Store the prompt used for this turn to update history later
        self._current_prompt_for_history = combined_content

        # Create worker and thread
        self.api_thread = QThread()
        self.api_worker = ApiWorker(
            model_name=model_name,
            temperature=temperature,
            prompt=combined_content, # Pass the final combined content
            history=self.dialogue_history if use_history_mode else None,
            image_paths=image_paths,
            use_history=use_history_mode
        )

        # Move worker to thread
        self.api_worker.moveToThread(self.api_thread)

        # Connect signals
        self.api_worker.new_chunk_received.connect(self.handle_new_chunk)
        self.api_worker.request_finished.connect(self.handle_request_finished)
        self.api_worker.request_error.connect(self.handle_request_error)
        self.api_thread.started.connect(self.api_worker.run_request)
        self.api_thread.finished.connect(self.cleanup_api_thread) # Connect thread finished to cleanup

        # Start the thread
        self.api_thread.start()

    # --- Slot Methods for Worker Signals ---
    @pyqtSlot(str)
    def handle_new_chunk(self, chunk):
        """Append received text chunk to the output area."""
        self.output_area.append_text(chunk)

    @pyqtSlot(str)
    def handle_request_finished(self, full_response):
        """Handle successful API request completion."""
        self.output_area.set_status(STRINGS[self.parent.current_lang]['response_received'])
        # Reset buttons immediately upon finishing successfully
        self.output_area.stop_button.setVisible(False)
        self.output_area.stop_button.setEnabled(False)
        self.output_area.copy_button.setVisible(True)
        self.output_area.copy_button.setEnabled(True)

        # Update dialogue history if in continuous mode
        if src.config.config.ENABLE_CONTINUOUS_DIALOGUE:
            # Add user message (the prompt we sent)
            if self._current_prompt_for_history:
                 # Ensure system prompt exists if history was empty
                 if not self.dialogue_history:
                     self.dialogue_history.append(("system", "You are a helpful assistant analyzing transcripts from meetings or conversations."))
                 self.dialogue_history.append(("user", self._current_prompt_for_history))

            # Add assistant message
            if full_response:
                self.dialogue_history.append(("assistant", full_response))

            # Truncate history if needed (logic moved from api.py)
            max_history = src.config.config.MAX_CONTEXT_MESSAGES
            if len(self.dialogue_history) > max_history:
                if src.config.config.SUMMARIZE_CONTEXT:
                    # (Keep summarization logic if needed, similar to api.py)
                    # For simplicity, just truncate for now
                    print(f"History truncated from {len(self.dialogue_history)} to {max_history}")
                    self.dialogue_history = self.dialogue_history[-max_history:]
                else:
                    print(f"History truncated from {len(self.dialogue_history)} to {max_history}")
                    self.dialogue_history = self.dialogue_history[-max_history:]

        self._current_prompt_for_history = "" # Clear the stored prompt

        # No need to call cleanup here, it's connected to thread.finished

    @pyqtSlot(str)
    def handle_request_error(self, error_message):
        """Handle API request errors."""
        self.output_area.set_status(f"{STRINGS[self.parent.current_lang]['model_call_error']}{error_message}", is_error=True)
        # Reset buttons immediately upon error
        self.output_area.stop_button.setVisible(False)
        self.output_area.stop_button.setEnabled(False)
        self.output_area.copy_button.setVisible(True)
        self.output_area.copy_button.setEnabled(True)
        self._current_prompt_for_history = "" # Clear the stored prompt

    def cleanup_api_thread(self):
        """Clean up thread and worker objects after thread finishes."""
        print("Cleaning up API thread...")
        # It's safer to check if the widgets still exist before accessing them,
        # especially if the window could be closed during the request.
        if hasattr(self, 'output_area') and self.output_area:
            # Reset button states after thread finishes (success, error, or stopped)
            self.output_area.stop_button.setVisible(False)
            self.output_area.stop_button.setEnabled(False)
            self.output_area.copy_button.setVisible(True)
            self.output_area.copy_button.setEnabled(True) # Ensure copy button is re-enabled

        # Clean up thread and worker objects
        if self.api_worker:
            self.api_worker.deleteLater()
        if self.api_thread:
            # Disconnect signals before deleting to avoid potential issues
            try:
                 self.api_thread.started.disconnect(self.api_worker.run_request)
                 self.api_thread.finished.disconnect(self.cleanup_api_thread)
                 self.api_worker.new_chunk_received.disconnect(self.handle_new_chunk)
                 self.api_worker.request_finished.disconnect(self.handle_request_finished)
                 self.api_worker.request_error.disconnect(self.handle_request_error)
            except TypeError: # Signals might already be disconnected
                 pass
            self.api_thread.deleteLater()

        self.api_thread = None
        self.api_worker = None


    def stop_api_request(self):
         """Request the worker to stop and wait for the thread to finish."""
         if self.api_worker:
             print("Requesting API worker stop...")
             self.api_worker.stop()
         if self.api_thread and self.api_thread.isRunning():
             print("Waiting for API thread to finish...")
             self.api_thread.quit()
             self.api_thread.wait() # Wait for thread to finish cleanly
             print("API thread finished.")
         else:
             # If thread wasn't running, ensure cleanup happens
             self.cleanup_api_thread()


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

    # Ensure worker is stopped if the widget is closed/destroyed
    def closeEvent(self, event):
        self.stop_api_request()
        super().closeEvent(event)