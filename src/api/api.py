import openai
import base64
from src.config.config import get_provider_info
from PyQt6.QtWidgets import QApplication
from src.gui.lang import STRINGS

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

def fetch_model_response(prompt, content_area, model_name, temperature, image_path=None):
    """
    从API获取模型的回复
    
    参数:
    - prompt: 提示文本
    - content_area: ContentArea实例，用于显示回复文本
    - model_name: 使用的模型名称
    - temperature: 温度参数
    - image_path: 可选的图片路径
    """
    try:
        # 首先清空输出
        content_area.clear_output()
        
        # Prepare base message content
        user_message = {"role": "user", "content": []}
        
        # Add text content
        if prompt:
            user_message["content"].append({
                "type": "text", 
                "text": prompt
            })
        
        # 检查是否使用支持视觉的模型并且有图像路径
        has_image = False
        # Add image content if provided and model supports vision
        if image_path and any(vision_model in model_name for vision_model in ["vision", "VL", "gemini", "claude", "gpt-4"]):
            base64_image = encode_image_to_base64(image_path)
            if base64_image:
                user_message["content"].append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                })
                has_image = True
        
        # If no vision capabilities needed, revert to simpler format
        if not image_path or len(user_message["content"]) == 1 and user_message["content"][0]["type"] == "text":
            user_message = {"role": "user", "content": prompt}

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
        
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            # 使用content_area的append_text方法添加文本，支持Markdown渲染
            content_area.append_text(delta)

    except Exception as e:
        main_window = QApplication.instance().activeWindow()
        lang = main_window.current_lang if main_window else 'zh'
        error_message = f"{STRINGS[lang]['model_call_error']}{str(e)}"
        content_area.clear_output()
        content_area.append_text(error_message)
