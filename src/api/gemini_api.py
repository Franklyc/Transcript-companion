import os
import base64
from google import genai
from google.genai import types
import src.config.config

# 辅助函数定义
def get_auxiliary_mode_prompt(mode):
    """
    根据选定的附加模式返回相应的提示词
    
    参数:
    - mode: 附加模式名称
    
    返回:
    - str: 附加模式对应的提示词，如果模式为none则返回空字符串
    """
    if mode == "none":
        return ""
    elif mode == "coding-solution":
        return src.config.config.CODING_SOLUTION_PROMPT
    elif mode == "coding-debug-general":
        return src.config.config.CODING_DEBUG_GENERAL_PROMPT
    elif mode == "coding-debug-correction":
        return src.config.config.CODING_DEBUG_CORRECTION_PROMPT
    elif mode == "coding-debug-time-optimize":
        return src.config.config.CODING_DEBUG_TIME_PROMPT
    elif mode == "coding-debug-space-optimize":
        return src.config.config.CODING_DEBUG_SPACE_PROMPT
    elif mode == "meeting-summarizer":
        return src.config.config.MEETING_SUMMARIZER_PROMPT
    elif mode == "action-item-extractor":
        return src.config.config.ACTION_ITEM_EXTRACTOR_PROMPT
    elif mode == "topic-tracker":
        return src.config.config.TOPIC_TRACKER_PROMPT
    elif mode == "sentiment-analyzer":
        return src.config.config.SENTIMENT_ANALYZER_PROMPT
    elif mode == "question-generator":
        return src.config.config.QUESTION_GENERATOR_PROMPT
    return ""

def encode_image_to_base64(image_path):
    """Encode an image file to base64 string"""
    if not image_path:
        return None
        
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def fetch_gemini_response(prompt, content_area, model_name, temperature, 
                          image_paths=None, use_search=False, system_instruction=""):
    """
    从Gemini API获取模型的回复
    
    参数:
    - prompt: 提示文本
    - content_area: ContentArea实例，用于显示回复文本
    - model_name: 使用的模型名称
    - temperature: 温度参数
    - image_paths: 可选的图片路径列表
    - use_search: 是否启用Google搜索功能
    - system_instruction: 系统指令
    """
    try:
        # 首先清空输出
        content_area.clear_output()
        
        # 检查是否启用了附加模式
        aux_mode = src.config.config.CURRENT_AUXILIARY_MODE
        aux_prompt = get_auxiliary_mode_prompt(aux_mode)
        
        # 如果启用了附加模式，将附加提示词添加到prompt后面
        if aux_prompt and prompt:
            final_prompt = f"{prompt}\n\n{aux_prompt}"
        else:
            final_prompt = prompt
        
        # 设置API客户端
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        
        # 提取真实的模型名称（去掉前缀）
        clean_model_name = model_name[model_name.index("]") + 2:]
        
        # 构建历史消息
        contents = []
        
        # 添加系统指令（如果有的话）
        if system_instruction:
            contents.append(
                types.Content(
                    role="user", 
                    parts=[types.Part.from_text(text="你是一个专业的助手")]
                )
            )
            contents.append(
                types.Content(
                    role="model",
                    parts=[types.Part.from_text(text="我是一个专业的助手，有什么我可以帮您的？")]
                )
            )
        
        # 处理用户输入
        user_parts = []
        
        # 添加文本内容
        if final_prompt:
            user_parts.append(types.Part.from_text(text=final_prompt))
            
        # 添加图片内容（如果有的话）
        if image_paths and isinstance(image_paths, list):
            for img_path in image_paths:
                if os.path.exists(img_path):
                    # 使用 files.upload 上传图片
                    uploaded_file = client.files.upload(file=img_path)
                    # 使用 from_uri 引用上传的图片
                    image_part = types.Part.from_uri(
                        file_uri=uploaded_file.uri,
                        mime_type=uploaded_file.mime_type
                    )
                    user_parts.append(image_part)
        
        # 将用户内容添加到消息中
        contents.append(
            types.Content(
                role="user",
                parts=user_parts
            )
        )
        
        # 配置请求参数
        generate_content_config = types.GenerateContentConfig(
            temperature=float(temperature),
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
            response_mime_type="text/plain",
            system_instruction=[
                types.Part.from_text(text=system_instruction if system_instruction else "你是一个专业的助手，分析会议或对话记录")
            ],
        )
        
        # 如果启用了搜索功能，添加搜索工具
        if use_search:
            generate_content_config.tools = [types.Tool(google_search=types.GoogleSearch())]
        
        # 发送请求并获取响应流
        response_stream = client.models.generate_content_stream(
            model=clean_model_name,
            contents=contents,
            config=generate_content_config,
        )
        
        # 存储完整回复
        full_response = ""
        
        # 处理流式响应
        for chunk in response_stream:
            if hasattr(chunk, 'text'):
                delta = chunk.text or ""
                full_response += delta
                # 使用content_area的append_text方法添加文本，支持Markdown渲染
                content_area.append_text(delta)
                
        # 返回完整的响应文本（用于对话历史记录）
        return full_response
                
    except Exception as e:
        error_message = f"Gemini API调用错误：{str(e)}"
        content_area.clear_output()
        content_area.append_text(error_message)
        return error_message

def fetch_gemini_response_with_history(prompt, content_area, model_name, temperature, 
                                       history, image_paths=None, use_search=False, system_instruction=""):
    """
    从Gemini API获取模型的回复，支持连续对话
    
    参数:
    - prompt: 当前提示文本
    - content_area: ContentArea实例
    - model_name: 使用的模型名称
    - temperature: 温度参数
    - history: 对话历史记录 [(role, content), ...]
    - image_paths: 可选的图片路径列表
    - use_search: 是否启用Google搜索功能
    - system_instruction: 系统指令
    """
    try:
        # 首先清空输出
        content_area.clear_output()
        
        # 检查是否启用了附加模式
        aux_mode = src.config.config.CURRENT_AUXILIARY_MODE
        aux_prompt = get_auxiliary_mode_prompt(aux_mode)
        
        # 如果启用了附加模式，将附加提示词添加到prompt后面
        if aux_prompt and prompt:
            final_prompt = f"{prompt}\n\n{aux_prompt}"
        else:
            final_prompt = prompt
        
        # 设置API客户端
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        
        # 提取真实的模型名称（去掉前缀）
        clean_model_name = model_name[model_name.index("]") + 2:]
        
        # 构建历史消息
        contents = []
        
        # 添加系统指令和历史消息
        has_system = False
        for role, content in history:
            if role == "system":
                has_system = True
                # 系统指令已经在配置中设置，这里不需要添加到messages中
                continue
            
            if role == "user":
                user_parts = [types.Part.from_text(text=content)]
                contents.append(types.Content(role="user", parts=user_parts))
            elif role == "assistant":
                assistant_parts = [types.Part.from_text(text=content)]
                contents.append(types.Content(role="model", parts=assistant_parts))
        
        # 处理当前用户输入
        user_parts = []
        
        # 添加文本内容
        if final_prompt:
            user_parts.append(types.Part.from_text(text=final_prompt))
            
        # 添加图片内容（如果有的话）
        if image_paths and isinstance(image_paths, list):
            for img_path in image_paths:
                if os.path.exists(img_path):
                    # 使用 files.upload 上传图片
                    uploaded_file = client.files.upload(file=img_path)
                    # 使用 from_uri 引用上传的图片
                    image_part = types.Part.from_uri(
                        file_uri=uploaded_file.uri,
                        mime_type=uploaded_file.mime_type
                    )
                    user_parts.append(image_part)
        
        # 将当前用户内容添加到消息中
        contents.append(
            types.Content(
                role="user",
                parts=user_parts
            )
        )
        
        # 配置请求参数
        generate_content_config = types.GenerateContentConfig(
            temperature=float(temperature),
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
            response_mime_type="text/plain",
            system_instruction=[
                types.Part.from_text(text=system_instruction if system_instruction else "你是一个专业的助手，分析会议或对话记录")
            ],
        )
        
        # 如果启用了搜索功能，添加搜索工具
        if use_search:
            generate_content_config.tools = [types.Tool(google_search=types.GoogleSearch())]
        
        # 发送请求并获取响应流
        response_stream = client.models.generate_content_stream(
            model=clean_model_name,
            contents=contents,
            config=generate_content_config,
        )
        
        # 存储完整回复
        full_response = ""
        
        # 处理流式响应
        for chunk in response_stream:
            if hasattr(chunk, 'text'):
                delta = chunk.text or ""
                full_response += delta
                # 使用content_area的append_text方法添加文本，支持Markdown渲染
                content_area.append_text(delta)
                
        # 返回完整的响应文本（用于更新对话历史记录）
        return full_response
                
    except Exception as e:
        error_message = f"Gemini API调用错误：{str(e)}"
        content_area.clear_output()
        content_area.append_text(error_message)
        return error_message