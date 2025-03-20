import openai
import base64
import json
from src.config.config import get_provider_info
from PyQt6.QtWidgets import QApplication
from src.gui.lang import STRINGS
import src.config.config
from src.api.gemini_api import fetch_gemini_response, fetch_gemini_response_with_history, get_auxiliary_mode_prompt


def _get_openai_client(model_name):
    provider_info = get_provider_info(model_name)
    if (provider_info):
        client = openai.OpenAI(
            base_url=provider_info.base_url,
            api_key=provider_info.api_key
        )
        clean_model_name = model_name[model_name.index("]") + 2:]
        return client, clean_model_name
    return openai.OpenAI(), model_name

def encode_image_to_base64(image_path):
    """Encode an image file to base64 string"""
    if not image_path:
        return None
        
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def fetch_model_response(prompt, content_area, model_name, temperature, image_paths=None):
    """
    从API获取模型的回复
    
    参数:
    - prompt: 提示文本
    - content_area: ContentArea实例，用于显示回复文本
    - model_name: 使用的模型名称
    - temperature: 温度参数
    - image_paths: 可选的图片路径列表
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
        
        # 检查是否为Gemini模型
        if "[Gemini]" in model_name:
            # 使用Gemini API
            return fetch_gemini_response(
                final_prompt, 
                content_area, 
                model_name, 
                temperature, 
                image_paths=image_paths, 
                use_search=src.config.config.ENABLE_GEMINI_SEARCH
            )
        
        # 以下是原始的OpenAI API处理逻辑
        # Prepare base message content
        user_message = {"role": "user", "content": []}
        
        # Add text content
        if final_prompt:
            user_message["content"].append({
                "type": "text", 
                "text": final_prompt
            })
        
        # 检查是否使用支持视觉的模型并且有图像路径
        has_image = False
        # Add image content if provided and model supports vision
        if image_paths and any(vision_model in model_name for vision_model in ["vision", "VL", "gemini", "claude", "gpt-4"]):
            # 处理图像列表
            if isinstance(image_paths, str):
                # 兼容旧代码，如果只是单个字符串路径
                image_paths = [image_paths]
                
            for img_path in image_paths:
                base64_image = encode_image_to_base64(img_path)
                if base64_image:
                    user_message["content"].append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    })
                    has_image = True
        
        # If no vision capabilities needed, revert to simpler format
        if not has_image and len(user_message["content"]) == 1 and user_message["content"][0]["type"] == "text":
            user_message = {"role": "user", "content": final_prompt}

        # 根据是否包含图像来决定是否添加系统消息
        messages = []
        if not has_image:
            messages.append({"role": "system", "content": ""})
        
        messages.append(user_message)

        params = {
            "messages": messages,
            "stream": True,
            "temperature": float(temperature),
            "top_p": 1
        }

        client, model_name = _get_openai_client(model_name)
        params["model"] = model_name

        # Special handling for specific providers
        if model_name.startswith("cerebras"):
            params["max_completion_tokens"] = 8192

        stream = client.chat.completions.create(**params)
        
        # 存储完整回复内容用于更新历史记录
        full_response = ""
        
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_response += delta
            # 使用content_area的append_text方法添加文本，支持Markdown渲染
            content_area.append_text(delta)
            
        # 如果启用了连续对话功能，需要记录对话历史
        if hasattr(content_area.parent.parent, 'content_area') and src.config.config.ENABLE_CONTINUOUS_DIALOGUE:
            dialogue_history = content_area.parent.parent.content_area.dialogue_history
            
            # 如果历史记录为空，添加系统消息
            if not dialogue_history and prompt:
                dialogue_history.append(("system", "You are a helpful assistant analyzing transcripts from meetings or conversations."))
            
            # 添加用户消息
            if prompt:
                dialogue_history.append(("user", prompt))
            
            # 添加助手消息
            if full_response:
                dialogue_history.append(("assistant", full_response))
                
            # 如果历史太长，保留最近的消息
            max_history = src.config.config.MAX_CONTEXT_MESSAGES
            if len(dialogue_history) > max_history:
                dialogue_history = dialogue_history[-max_history:]
                
            # 更新到内容区域
            content_area.parent.parent.content_area.dialogue_history = dialogue_history
            
        return full_response

    except Exception as e:
        main_window = QApplication.instance().activeWindow()
        lang = main_window.current_lang if main_window else 'zh'
        error_message = f"{STRINGS[lang]['model_call_error']}{str(e)}"
        content_area.clear_output()
        content_area.append_text(error_message)
        return error_message

def fetch_model_response_with_history(prompt, content_area, model_name, temperature, history, image_paths=None):
    """
    从API获取模型的回复，支持连续对话
    
    参数:
    - prompt: 当前提示文本
    - content_area: ContentArea实例
    - model_name: 使用的模型名称
    - temperature: 温度参数
    - history: 对话历史记录 [(role, content), ...]
    - image_paths: 可选的图片路径列表
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
        
        # 检查是否为Gemini模型
        if "[Gemini]" in model_name:
            # 使用Gemini API
            return fetch_gemini_response_with_history(
                final_prompt, 
                content_area, 
                model_name, 
                temperature, 
                history,
                image_paths=image_paths, 
                use_search=src.config.config.ENABLE_GEMINI_SEARCH
            )
        
        # 以下是原始的OpenAI API处理逻辑
        # 构建消息数组
        messages = []
        
        # 添加系统消息
        if not history or history[0][0] != "system":
            messages.append({"role": "system", "content": "You are a helpful assistant analyzing transcripts from meetings or conversations."})
        
        # 添加历史消息
        for role, content in history:
            if role in ["system", "user", "assistant"]:
                messages.append({"role": role, "content": content})
        
        # 添加当前用户消息（支持图像）
        if final_prompt:
            # 创建用户消息
            user_message = {"role": "user", "content": []}
            
            # 添加文本内容
            if final_prompt:
                user_message["content"].append({
                    "type": "text", 
                    "text": final_prompt
                })
            
            # 添加图片内容
            has_image = False
            if image_paths and any(vision_model in model_name for vision_model in ["vision", "VL", "gemini", "claude", "gpt-4"]):
                if isinstance(image_paths, str):
                    image_paths = [image_paths]
                    
                for img_path in image_paths:
                    base64_image = encode_image_to_base64(img_path)
                    if base64_image:
                        user_message["content"].append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        })
                        has_image = True
            
            # 如果没有图片，使用简单格式
            if not has_image and len(user_message["content"]) == 1 and user_message["content"][0]["type"] == "text":
                user_message = {"role": "user", "content": final_prompt}
                
            messages.append(user_message)
        
        params = {
            "messages": messages,
            "stream": True,
            "temperature": float(temperature),
            "top_p": 1
        }

        client, model_name = _get_openai_client(model_name)
        params["model"] = model_name

        # 特殊处理特定提供商
        if model_name.startswith("cerebras"):
            params["max_completion_tokens"] = 8192

        stream = client.chat.completions.create(**params)
        
        # 存储完整回复内容用于更新历史记录
        full_response = ""
        
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_response += delta
            # 使用content_area的append_text方法添加文本，支持Markdown渲染
            content_area.append_text(delta)
            
        # 更新对话历史
        if history is not None:
            # 添加用户消息（如果有）
            if prompt:  # 注意这里保存原始的prompt，不包含附加提示词
                history.append(("user", prompt))
                
            # 添加助手消息
            if full_response:
                history.append(("assistant", full_response))
                
            # 如果历史太长，保留最近的消息
            max_history = src.config.config.MAX_CONTEXT_MESSAGES
            if len(history) > max_history:
                if src.config.config.SUMMARIZE_CONTEXT:
                    # 保留系统消息，但创建一个早期消息的摘要
                    system_msg = None
                    if history[0][0] == "system":
                        system_msg = history[0]
                        
                    # 创建摘要的内容
                    summary = "Previous conversation summary:\n"
                    for i, (role, content) in enumerate(history[:len(history) - max_history + 2]):
                        if i == 0 and role == "system":
                            continue  # 跳过系统消息
                        summary += f"{role}: {content[:100]}...\n"
                    
                    # 重建历史记录
                    new_history = []
                    if system_msg:
                        new_history.append(system_msg)
                    new_history.append(("system", summary))
                    new_history.extend(history[-(max_history-2):])
                    history[:] = new_history
                else:
                    # 简单地保留最近的消息
                    history[:] = history[-max_history:]
        
        return full_response
                
    except Exception as e:
        main_window = QApplication.instance().activeWindow()
        lang = main_window.current_lang if main_window else 'zh'
        error_message = f"{STRINGS[lang]['model_call_error']}{str(e)}"
        content_area.clear_output()
        content_area.append_text(error_message)
        return error_message
