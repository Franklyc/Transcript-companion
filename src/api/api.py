import openai
import base64
from src.config.config import get_provider_info
from PyQt6.QtWidgets import QApplication
from src.gui.lang import STRINGS

def _get_openai_client(model_name):
    provider_info = get_provider_info(model_name)
    if provider_info:
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

def fetch_model_response(prompt, output_textbox, model_name, temperature, image_path=None):
    try:
        # Prepare base message content
        user_message = {"role": "user", "content": []}
        
        # Add text content
        if prompt:
            user_message["content"].append({
                "type": "text", 
                "text": prompt
            })
        
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
        
        # If no vision capabilities needed, revert to simpler format
        if not image_path or len(user_message["content"]) == 1 and user_message["content"][0]["type"] == "text":
            user_message = {"role": "user", "content": prompt}

        params = {
            "messages": [
                {"role": "system", "content": ""},
                user_message
            ],
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
        output_textbox.clear()
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            output_textbox.insertPlainText(delta)
            QApplication.processEvents()

    except Exception as e:
        output_textbox.clear()
        main_window = QApplication.instance().activeWindow()
        lang = main_window.current_lang if main_window else 'zh'
        output_textbox.insertPlainText(f"{STRINGS[lang]['model_call_error']}{e}")
        QApplication.processEvents()
