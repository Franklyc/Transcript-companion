STRINGS = {
    'zh': {
        'window_title': "Transcript companion",
        'current_folder': "当前文件夹:",
        'select_folder': "选择文件夹",
        'select_model': "选择模型:",
        'set_temperature': "设置温度 (0.0-1.5):",
        'custom_prefix': "自定义前缀:",
        'custom_suffix': "自定义后缀:",
        'copy_and_get_answer': "复制并获取回答",
        'copied_success': "已复制最新文件内容！",
        'file_path': "文件路径: ",
        'read_file_error': "读取文件失败: ",
        'no_files_available': "目录中没有可用的文件！",
        'help_title': '帮助',
        'help_text': '''
使用说明：
1. 选择文件夹：选择存放语音转写文件的目录
2. 选择模型：选择要使用的AI模型
3. 设置温度：调整AI回答的创造性（0.0-2.0）
4. 自定义前缀/后缀：添加额外的提示内容
5. 点击"复制并获取回答"开始处理
6. 使用截图功能添加图片到提问

侧边栏功能：
🀄/🔤 - 切换中英文
🌙/☀️ - 切换深浅主题
❓ - 显示帮助
⚙️ - 设置
🗑️ - 清除内容
🔄 - 刷新本地模型列表（用于LMstudio/Kobold/Ollama）
''',
        'settings_title': '设置',
        'use_predefined_prefix': '使用预定义前缀',
        'use_transcript_text': '使用转录文件内容',
        'select_provider': '选择服务提供商:',
        'model_call_error': "调用模型失败: ",
        'export_conversation': "导出对话",
        'export_success': "对话已成功导出到 history 文件夹！",
        'export_error': "导出对话失败: ",
        'ocr_screenshot': "截图并OCR",
        'ocr_text': "OCR文本 (可编辑):",
        'ocr_instructions': "使用鼠标左键拖动选择屏幕区域进行OCR。再次点击以取消。",
        'ocr_success': "OCR 完成！",
        'ocr_error': "OCR 失败",
        'ocr_selection_canceled': "OCR 截图已取消。",
        'image_upload': "上传图片",
        'image_upload_success': "图片已成功上传！",
        'image_upload_error': "上传图片失败: ",
        'screenshot_capture': "区域截图",
        'fullscreen_capture': "全屏截图",
        'screenshot_instructions': "使用鼠标左键拖动选择屏幕区域进行截图。再次点击以取消。",
        'screenshot_success': "截图已捕获！",
        'screenshot_canceled': "截图已取消。",
        'image_preview': "图片预览:",
        'image_clear': "清除图片",
        'clear_all_images': "清除所有图片",
        'use_image': "使用图片与模型交流",
        'tab_settings': "设置",
        'tab_input': "输入",
        'output_result': "输出结果:",
        'show_source': "显示源文本",
        'remove_image': "移除图片",
        'add_more_images': "添加更多图片",
        
        # 连续对话相关文本
        'enable_continuous_dialogue': "启用连续对话",
        'continuous_dialogue_enabled': "连续对话已启用",
        'continuous_dialogue_disabled': "连续对话已禁用",
        'new_content_detected': "检测到新内容，长度: {0}字符",
        'resuming_from_position': "从上次位置继续: {0}",
        'continuous_dialogue_context': "上下文中包含 {0} 条消息",
        'reset_dialogue_context': "重置对话上下文",
        'reset_position': "重置文件位置",
        'reset_position_success': "已重置文件位置，将从文件开头读取",
          # Gemini搜索相关文本
        'enable_gemini_search': "为Gemini模型启用Google搜索",
        'gemini_search_enabled': "Gemini Google搜索功能已启用",
        'gemini_search_disabled': "Gemini Google搜索功能已禁用",
        
        # Gemini思考预算相关文本
        'gemini_thinking_budget_title': "Gemini思考预算设置",
        'gemini_thinking_budget_label': "思考预算 (0-24576):",
        'gemini_thinking_budget_description': "仅支持gemini-2.5-flash-preview模型",
        'gemini_thinking_budget_saved': "Gemini思考预算已更新为: {0}",
        
        # 附加模式相关文本
        'select_auxiliary_mode': "选择附加模式:",
        'auxiliary_mode_none': "无",
        'auxiliary_mode_coding_solution': "编码问题-初步解法",
        'auxiliary_mode_coding_debug_general': "编码问题-通用调试",
        'auxiliary_mode_coding_debug_correction': "编码问题-代码改正",
        'auxiliary_mode_coding_debug_time_optimize': "编码问题-时间复杂度优化",
        'auxiliary_mode_coding_debug_space_optimize': "编码问题-空间复杂度优化",
        'auxiliary_mode_meeting_summarizer': "会议-总结要点",
        'auxiliary_mode_action_item_extractor': "会议-提取行动项目",
        'auxiliary_mode_topic_tracker': "会议-主题追踪",
        'auxiliary_mode_sentiment_analyzer': "会议-情感分析",
        'auxiliary_mode_question_generator': "会议-问题生成",
        'auxiliary_mode_changed': "附加模式已更改为: {0}",
    },
    'en': {
        'window_title': "Transcript companion",
        'current_folder': "Current Folder:",
        'select_folder': "Select Folder",
        'select_model': "Select Model:",
        'set_temperature': "Temperature (0.0-1.5):",
        'custom_prefix': "Custom Prefix:",
        'custom_suffix': "Custom Suffix:",
        'copy_and_get_answer': "Copy and Get Answer",
        'copied_success': "Latest file content copied!",
        'file_path': "File path: ",
        'read_file_error': "Failed to read file: ",
        'no_files_available': "No files available in the directory!",
        'help_title': 'Help',
        'help_text': '''
Instructions:
1. Select Folder: Choose directory for speech transcription files
2. Select Model: Choose AI model to use
3. Set Temperature: Adjust AI response creativity (0.0-2.0)
4. Custom Prefix/Suffix: Add additional prompts
5. Click "Copy and Get Answer" to start
6. Use screenshot feature to include images in questions

Sidebar Features:
🀄/🔤 - Toggle Language
🌙/☀️ - Toggle Theme
❓ - Show Help
⚙️ - Settings
🗑️ - Clear Content
🔄 - Refresh Local Models (for LMstudio/Kobold/Ollama)
''',
        'settings_title': 'Settings',
        'use_predefined_prefix': 'Use Predefined Prefix',
        'use_transcript_text': 'Use Transcript Text',
        'select_provider': 'Select Provider:',
        'model_call_error': "Failed to call model: ",
        'export_conversation': "Export Conversation",
        'export_success': "Conversation successfully exported to history folder!",
        'export_error': "Failed to export conversation: ",
        'ocr_screenshot': "OCR Capture",
        'ocr_text': "OCR Text (Editable):",
        'ocr_instructions': "Click and drag the left mouse button to select a screen area for OCR. Click again to cancel.",
        'ocr_success': "OCR Completed!",
        'ocr_error': "OCR Failed",
        'ocr_selection_canceled': "OCR screenshot canceled.",
        'image_upload': "Upload Pic",
        'image_upload_success': "Image successfully uploaded!",
        'image_upload_error': "Failed to upload image: ",
        'screenshot_capture': "Area Shot",
        'fullscreen_capture': "Full Shot",
        'screenshot_instructions': "Click and drag the left mouse button to select a screen area for screenshot. Click again to cancel.",
        'screenshot_success': "Screenshot captured!",
        'screenshot_canceled': "Screenshot canceled.",
        'image_preview': "Image Preview:",
        'image_clear': "Clear",
        'clear_all_images': "Clear All Pics",
        'use_image': "Use Image with Model",
        'tab_settings': "Settings",
        'tab_input': "Input",
        'output_result': "Output Result:",
        'show_source': "Show Source",
        'remove_image': "Remove",
        'add_more_images': "Add More Images",
        
        # 连续对话相关文本
        'enable_continuous_dialogue': "Enable Continuous Dialogue",
        'continuous_dialogue_enabled': "Continuous Dialogue Enabled",
        'continuous_dialogue_disabled': "Continuous Dialogue Disabled",
        'new_content_detected': "New content detected, length: {0} characters",
        'resuming_from_position': "Resuming from previous position: {0}",
        'continuous_dialogue_context': "Context includes {0} messages",
        'reset_dialogue_context': "Reset Dialogue Context",
        'reset_position': "Reset File Position",
        'reset_position_success': "File position reset, will start reading from the beginning",
          # Gemini搜索相关文本
        'enable_gemini_search': "Enable Google Search for Gemini models",
        'gemini_search_enabled': "Gemini Google Search feature enabled",
        'gemini_search_disabled': "Gemini Google Search feature disabled",
        
        # Gemini思考预算相关文本
        'gemini_thinking_budget_title': "Gemini Thinking Budget Settings",
        'gemini_thinking_budget_label': "Thinking Budget (0-24576):",
        'gemini_thinking_budget_description': "Only supported for gemini-2.5-flash-preview model",
        'gemini_thinking_budget_saved': "Gemini thinking budget updated to: {0}",
        
        # 附加模式相关文本
        'select_auxiliary_mode': "Select Auxiliary Mode:",
        'auxiliary_mode_none': "None",
        'auxiliary_mode_coding_solution': "Coding Problem - Solution",
        'auxiliary_mode_coding_debug_general': "Coding Problem - General Debug",
        'auxiliary_mode_coding_debug_correction': "Coding Problem - Code Correction",
        'auxiliary_mode_coding_debug_time_optimize': "Coding Problem - Time Complexity Optimization",
        'auxiliary_mode_coding_debug_space_optimize': "Coding Problem - Space Complexity Optimization",
        'auxiliary_mode_meeting_summarizer': "Meeting - Summarize Key Points",
        'auxiliary_mode_action_item_extractor': "Meeting - Extract Action Items",
        'auxiliary_mode_topic_tracker': "Meeting - Topic Tracking",
        'auxiliary_mode_sentiment_analyzer': "Meeting - Sentiment Analysis",
        'auxiliary_mode_question_generator': "Meeting - Question Generation",
        'auxiliary_mode_changed': "Auxiliary mode changed to: {0}",
    }
}