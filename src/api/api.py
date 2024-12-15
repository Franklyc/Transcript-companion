import openai
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

def fetch_model_response(prompt, output_textbox, model_name, temperature):
    try:
        params = {
            "messages": [
                {"role": "system", "content": ""},
                {"role": "user", "content": prompt},
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

        is_gemini = model_name.startswith("gemini")
        stream = client.chat.completions.create(**params)

        output_textbox.clear()
        for chunk in stream:
            if is_gemini:
                delta = chunk.choices[0].delta.content or ""
            else:
                delta = chunk.choices[0].delta.content or ""
            output_textbox.insertPlainText(delta)
            QApplication.processEvents()

    except Exception as e:
        output_textbox.clear()
        main_window = QApplication.instance().activeWindow()
        lang = main_window.current_lang if main_window else 'zh'
        output_textbox.insertPlainText(f"{STRINGS[lang]['model_call_error']}{e}")
        QApplication.processEvents()
